from __future__ import annotations

import json
import math
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

ADAPTER_SCHEMA_VERSION = "oif2.civilizational-state-adapter.v1"
MAX_SOURCE_BYTES = 8 * 1024 * 1024

EPISTEMIC_INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}


class CivilizationalStateFormatError(ValueError):
    pass


class CivilizationalStateAdapter:
    """Read-only translation of authoritative civilizational state files."""

    primitive = "OIF2_CIVILIZATIONAL_STATE_ADAPTER"

    def __init__(self, root: Optional[Path] = None) -> None:
        selected_root = (
            Path(root) if root is not None
            else Path.home() / "open-cognitive-ecology"
        )
        self.root = Path(os.path.abspath(str(selected_root.expanduser())))
        base = self.root / "representative_succession"
        self.sources = {
            "civilizational_identity": (
                base / "civilizational_identity_preservation.json"
            ),
            "representative_state": base / "representative_registry.json",
            "continuity_state": base / "continuity_metrics_engine.json",
            "succession_state": base / "succession_execution.json",
        }
        self._allowed_lexical_paths = frozenset(
            Path(os.path.abspath(str(path)))
            for path in self.sources.values()
        )

    def __call__(self) -> dict[str, Any]:
        return self.read()

    def _governed_paths(self, path: Path) -> tuple[Path, Path]:
        lexical = Path(os.path.abspath(str(path.expanduser())))
        if lexical not in self._allowed_lexical_paths:
            raise CivilizationalStateFormatError(
                f"source is not an allowed civilizational-state path: {path}"
            )
        try:
            lexical.relative_to(self.root)
        except ValueError as exc:
            raise CivilizationalStateFormatError(
                f"source escapes governed lexical root: {path}"
            ) from exc
        return lexical, lexical.resolve(strict=False)

    @staticmethod
    def _reject_constant(value: str) -> None:
        raise CivilizationalStateFormatError(
            f"non-finite JSON constant rejected: {value}"
        )

    @staticmethod
    def _validate_finite(value: Any, label: str) -> None:
        if isinstance(value, bool):
            return
        if isinstance(value, (int, float)):
            if not math.isfinite(float(value)):
                raise CivilizationalStateFormatError(
                    f"{label} must contain only finite numbers"
                )
            return
        if isinstance(value, Mapping):
            for key, child in value.items():
                CivilizationalStateAdapter._validate_finite(
                    child, f"{label}.{key}"
                )
            return
        if isinstance(value, list):
            for index, child in enumerate(value):
                CivilizationalStateAdapter._validate_finite(
                    child, f"{label}[{index}]"
                )

    @staticmethod
    def _fingerprint(path: Path) -> tuple[int, int, int] | None:
        if not path.exists() or not path.is_file():
            return None
        stat_result = path.stat()
        return (
            stat_result.st_mtime_ns,
            stat_result.st_size,
            stat_result.st_ino,
        )

    @staticmethod
    def _section_status(name: str, value: Mapping[str, Any]) -> str:
        if name == "civilizational_identity":
            if value.get("civilizational_identity_loss_detected") is True:
                return "degraded"
            if (
                value.get("civilizational_identity_preserved") is True
                and value.get("recovery_required") is False
            ):
                return "ready"
            return "unknown"

        if name == "representative_state":
            current = value.get("current_representative")
            if not isinstance(current, Mapping):
                return "unknown"
            central = current.get("representative_is_central")
            revocable = current.get("representative_is_revocable")
            status = str(current.get("status", "unknown")).strip().lower()
            civilization = str(
                current.get("civilization_identity", "")
            ).strip()
            representative_id = str(
                current.get("representative_id", "")
            ).strip()
            if central is True or revocable is False:
                return "degraded"
            if (
                central is False
                and revocable is True
                and status == "active"
                and civilization
                and representative_id
                and civilization != representative_id
            ):
                return "ready"
            return "unknown"

        if name == "continuity_state":
            if value.get("recovery_required") is True:
                return "degraded"
            decision = str(
                value.get("continuity_decision", "")
            ).strip().lower()
            validated = value.get("continuity_validated")
            if validated is False or "failure" in decision:
                return "degraded"
            if validated is True:
                return "ready"
            return "unknown"

        if name == "succession_state":
            event = value.get("latest_succession_event")
            if not isinstance(event, Mapping):
                event = value.get("succession_event")
            if not isinstance(event, Mapping):
                event = value
            execution_status = str(
                event.get("execution_status", "unknown")
            ).strip().lower()
            executed = event.get("succession_executed")
            continuity = event.get("civilizational_continuity_preserved")
            if execution_status in {"failed", "error"}:
                return "degraded"
            if executed is True and continuity is False:
                return "degraded"
            if execution_status in {
                "blocked", "not_requested", "ready", "completed"
            }:
                return "ready"
            if executed is False and execution_status == "unknown":
                return "unknown"
            return "ready" if executed is True else "unknown"

        return "unknown"

    def _read_source(self, name: str, path: Path) -> dict[str, Any]:
        lexical, resolved = self._governed_paths(path)
        descriptor: dict[str, Any] = {
            "name": name,
            "relative_path": str(lexical.relative_to(self.root)),
            "resolved_external_storage": not resolved.is_relative_to(
                self.root.resolve(strict=False)
            ),
            "read_only": True,
        }
        if not lexical.exists():
            descriptor.update({
                "availability": "missing",
                "status": "unavailable",
                "payload": None,
            })
            return descriptor
        if lexical.is_symlink():
            descriptor.update({
                "availability": "invalid",
                "status": "unavailable",
                "error_type": "DirectSourceSymlinkRejected",
                "payload": None,
            })
            return descriptor
        if not resolved.is_file():
            descriptor.update({
                "availability": "invalid",
                "status": "unavailable",
                "error_type": "UnsafeSource",
                "payload": None,
            })
            return descriptor
        size = resolved.stat().st_size
        descriptor["size_bytes"] = size
        if size > MAX_SOURCE_BYTES:
            descriptor.update({
                "availability": "invalid",
                "status": "unavailable",
                "error_type": "SourceTooLarge",
                "payload": None,
            })
            return descriptor
        try:
            value = json.loads(
                resolved.read_text(encoding="utf-8"),
                parse_constant=self._reject_constant,
            )
            if not isinstance(value, dict):
                raise CivilizationalStateFormatError(
                    f"{name} root must be a JSON object"
                )
            self._validate_finite(value, name)
        except Exception as exc:
            descriptor.update({
                "availability": "invalid",
                "status": "unavailable",
                "error_type": type(exc).__name__,
                "payload": None,
            })
            return descriptor
        descriptor.update({
            "availability": "available",
            "status": self._section_status(name, value),
            "payload": deepcopy(value),
        })
        return descriptor

    def read(self) -> dict[str, Any]:
        before = {
            name: self._fingerprint(path)
            for name, path in self.sources.items()
        }
        sections = {
            name: self._read_source(name, path)
            for name, path in self.sources.items()
        }
        after = {
            name: self._fingerprint(path)
            for name, path in self.sources.items()
        }
        if before != after:
            raise CivilizationalStateFormatError(
                "source changed during read; snapshot rejected"
            )

        available = sum(
            section["availability"] == "available"
            for section in sections.values()
        )
        invalid = sum(
            section["availability"] == "invalid"
            for section in sections.values()
        )
        degraded = any(
            section["status"] == "degraded"
            for section in sections.values()
        )
        if invalid:
            status = "degraded"
        elif available == 0:
            status = "unavailable"
        elif available < len(sections) or degraded:
            status = "degraded"
        else:
            status = "ready"

        return {
            "primitive": self.primitive,
            "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
            "status": status,
            "read_only": True,
            "translation_only": True,
            "producer_execution": False,
            "synthetic_cross_source_score": False,
            "species_representative_distinction_required": True,
            "external_storage_supported": True,
            "direct_source_symlinks_rejected": True,
            "source_count": len(sections),
            "available_source_count": available,
            "invalid_source_count": invalid,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "sections": sections,
            **EPISTEMIC_INVARIANTS,
        }
