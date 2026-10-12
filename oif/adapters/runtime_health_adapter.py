
from __future__ import annotations

import json
import math
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

ADAPTER_SCHEMA_VERSION = "oif2.runtime-health-adapter.v1"
MAX_SOURCE_BYTES = 4 * 1024 * 1024

EPISTEMIC_INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}


class RuntimeHealthFormatError(ValueError):
    pass


class RuntimeHealthAdapter:
    # Read-only translation of existing runtime and host-health state files.
    # Governed lexical paths may traverse an intentional parent-directory
    # symlink to external persistent storage. Direct source-file symlinks are
    # still rejected, and only the three fixed source paths are admissible.

    primitive = "OIF2_RUNTIME_HEALTH_ADAPTER"

    def __init__(self, root: Optional[Path] = None) -> None:
        selected_root = (
            Path(root) if root is not None
            else Path.home() / "open-cognitive-ecology"
        )
        self.root = Path(
            os.path.abspath(str(selected_root.expanduser()))
        )
        self.sources = {
            "runtime_service": self.root / "runtime_service/service_state.json",
            "long_duration_runtime": (
                self.root
                / "runtime_supervision/long_duration_runtime_state.json"
            ),
            "hardware_health": (
                self.root
                / "physical_ecology/latest_hardware_health_monitor.json"
            ),
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
            raise RuntimeHealthFormatError(
                f"source is not an allowed runtime-health path: {path}"
            )

        try:
            lexical.relative_to(self.root)
        except ValueError as exc:
            raise RuntimeHealthFormatError(
                f"source escapes governed lexical root: {path}"
            ) from exc

        resolved = lexical.resolve(strict=False)
        return lexical, resolved

    @staticmethod
    def _reject_constant(value: str) -> None:
        raise RuntimeHealthFormatError(
            f"non-finite JSON constant rejected: {value}"
        )

    @staticmethod
    def _validate_finite(value: Any, label: str) -> None:
        if isinstance(value, bool):
            return
        if isinstance(value, (int, float)):
            if not math.isfinite(float(value)):
                raise RuntimeHealthFormatError(
                    f"{label} must contain only finite numbers"
                )
            return
        if isinstance(value, Mapping):
            for key, child in value.items():
                RuntimeHealthAdapter._validate_finite(
                    child, f"{label}.{key}"
                )
            return
        if isinstance(value, list):
            for index, child in enumerate(value):
                RuntimeHealthAdapter._validate_finite(
                    child, f"{label}[{index}]"
                )

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
            raw = resolved.read_text(encoding="utf-8")
            value = json.loads(
                raw,
                parse_constant=self._reject_constant,
            )
            if not isinstance(value, dict):
                raise RuntimeHealthFormatError(
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
            "status": self._source_status(name, value),
            "payload": deepcopy(value),
        })
        return descriptor

    @staticmethod
    def _source_status(name: str, value: Mapping[str, Any]) -> str:
        if name == "hardware_health":
            classification = str(
                value.get("health_classification", "unknown")
            ).strip().lower()
            if classification in {"healthy", "nominal", "operational"}:
                return "ready"
            if classification in {
                "degraded", "warning", "critical", "failed"
            }:
                return "degraded"
            return "unknown"

        if name == "long_duration_runtime":
            viability = value.get("last_long_duration_viability")
            uptime = value.get("last_uptime_score")
            restart_events = value.get("restart_events")
            supervision_cycles = value.get("supervision_cycles")

            numeric_values = (
                viability,
                uptime,
                restart_events,
                supervision_cycles,
            )
            if any(
                isinstance(item, bool)
                or not isinstance(item, (int, float))
                for item in numeric_values
            ):
                return "unknown"

            viability = float(viability)
            uptime = float(uptime)
            restart_events = int(restart_events)
            supervision_cycles = int(supervision_cycles)

            if (
                viability >= 0.90
                and uptime >= 0.90
                and restart_events >= 0
                and supervision_cycles > 0
            ):
                return "ready"

            if (
                viability < 0.75
                or uptime < 0.75
                or restart_events < 0
                or supervision_cycles <= 0
            ):
                return "degraded"

            return "unknown"

        raw = str(value.get("status", "unknown")).strip().lower()
        if raw in {"running", "ready", "operational", "completed"}:
            return "ready"
        if raw in {
            "degraded", "warning", "failed", "error",
            "stopped_by_user", "stopped",
        }:
            return "degraded"
        return "unknown"

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
            raise RuntimeHealthFormatError(
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
            aggregate_status = "degraded"
        elif available == 0:
            aggregate_status = "unavailable"
        elif available < len(sections) or degraded:
            aggregate_status = "degraded"
        else:
            aggregate_status = "ready"

        return {
            "primitive": self.primitive,
            "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
            "status": aggregate_status,
            "read_only": True,
            "translation_only": True,
            "producer_execution": False,
            "synthetic_cross_source_score": False,
            "external_storage_supported": True,
            "direct_source_symlinks_rejected": True,
            "source_count": len(sections),
            "available_source_count": available,
            "invalid_source_count": invalid,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "sections": sections,
            **EPISTEMIC_INVARIANTS,
        }
