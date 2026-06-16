# -*- coding: utf-8 -*-


"""
E1 — Metrics History Recorder.

Canonical, append-only JSONL instrumentation layer for Open Cognitive Ecology.
It normalises runtime outputs into a common empirical schema and writes them to:

    ~/open-cognitive-ecology/metrics/metrics_history.jsonl

A compatibility mirror is also maintained at:

    ~/open-cognitive-ecology/metrics_history.jsonl

The primitive is intentionally conservative: it never raises on metric write
failure, preserves local disk usage with bounded rotation, and records only
functional, quantitative or status-oriented information.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import math
import os
import shutil
from typing import Any, Dict, Iterable, Optional

PRIMITIVE = "metrics_history_recorder"

DEPENDENCIES = [
    "civilizational_metrics_synthesizer",
    "enhanced_civilizational_metrics",
    "runtime_experiment_manager",
    "experiment_stability_dashboard",
    "scientific_anomaly_detector",
    "scientific_meta_analysis_engine",
    "consciousness_statistical_significance_engine",
]

DEFAULT_MAX_HISTORY_BYTES = 25 * 1024 * 1024
DEFAULT_MAX_LEGACY_BYTES = 10 * 1024 * 1024


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        try:
            return not (math.isnan(float(value)) or math.isinf(float(value)))
        except Exception:
            return False
    return False


def _safe_status(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    if isinstance(value, bool):
        return "validated" if value else "not_validated"
    text = str(value).strip()
    return text if text else default


class MetricsHistoryRecorder:
    """Append-only empirical metrics recorder with bounded local storage."""

    primitive = PRIMITIVE

    def __init__(
        self,
        root: str | Path | None = None,
        max_history_bytes: int = DEFAULT_MAX_HISTORY_BYTES,
        max_legacy_bytes: int = DEFAULT_MAX_LEGACY_BYTES,
    ) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.metrics_dir = self.root / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.metrics_dir / "metrics_history.jsonl"
        self.legacy_history_path = self.root / "metrics_history.jsonl"
        self.state_path = self.metrics_dir / "metrics_history_recorder_state.json"
        self.max_history_bytes = max(1024 * 1024, int(max_history_bytes))
        self.max_legacy_bytes = max(256 * 1024, int(max_legacy_bytes))

    def _read_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "record_count": 0,
            "rotation_count": 0,
            "last_record_timestamp": None,
        }

    def _write_state(self, state: dict[str, Any]) -> None:
        state["primitive"] = PRIMITIVE
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _rotate_if_needed(self, path: Path, max_bytes: int) -> bool:
        try:
            if not path.exists() or path.stat().st_size <= max_bytes:
                return False
            archive = path.with_suffix(path.suffix + ".bak")
            if archive.exists():
                archive.unlink()
            shutil.move(str(path), str(archive))
            return True
        except Exception:
            return False

    def _extract_metrics(self, payload: dict[str, Any]) -> dict[str, float | int]:
        metrics: dict[str, float | int] = {}

        explicit = payload.get("metrics")
        if isinstance(explicit, dict):
            for key, value in explicit.items():
                if _is_number(value):
                    metrics[str(key)] = value

        for key, value in payload.items():
            if key in {"metrics", "diagnostics", "latest_records", "records", "agent_result", "notification_result"}:
                continue
            if _is_number(value):
                metrics[str(key)] = value

        diagnostics = payload.get("diagnostics")
        if isinstance(diagnostics, dict):
            for key, value in diagnostics.items():
                if _is_number(value):
                    metrics[f"diagnostics.{key}"] = value

        return metrics

    def _infer_error_count(self, payload: dict[str, Any]) -> int:
        for key in ("error_count", "errors", "failed_calls", "failed_emissions"):
            value = payload.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                return max(0, int(value))
        diagnostics = payload.get("diagnostics")
        if isinstance(diagnostics, dict):
            value = diagnostics.get("error_count")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return max(0, int(value))
        if payload.get("error") or payload.get("exception"):
            return 1
        return 0

    def normalize(
        self,
        payload: dict[str, Any] | None = None,
        primitive: str | None = None,
        validation_status: str | bool | None = None,
        governance_status: str | bool | None = None,
        runtime_status: str | bool | None = None,
    ) -> dict[str, Any]:
        payload = dict(payload or {})
        source_primitive = primitive or payload.get("primitive") or payload.get("source") or "unknown"
        metrics = self._extract_metrics(payload)
        error_count = self._infer_error_count(payload)

        if validation_status is None:
            validation_status = payload.get("validation_status")
            if validation_status is None:
                validation_status = payload.get("validated") or payload.get("certified")
        if governance_status is None:
            governance_status = payload.get("governance_status")
            if governance_status is None:
                governance_status = payload.get("governance_allowed")
        if runtime_status is None:
            runtime_status = payload.get("runtime_status")
            if runtime_status is None:
                runtime_status = payload.get("status") or payload.get("operational")

        return {
            "timestamp": payload.get("timestamp") or payload.get("timestamp_utc") or _now(),
            "primitive": str(source_primitive).lower(),
            "metrics": metrics,
            "validation_status": _safe_status(validation_status),
            "governance_status": _safe_status(governance_status),
            "runtime_status": _safe_status(runtime_status),
            "error_count": error_count,
            "source_payload_keys": sorted(str(k) for k in payload.keys())[:200],
        }

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        serialized = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        rotations = 0
        if self._rotate_if_needed(self.history_path, self.max_history_bytes):
            rotations += 1
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(serialized)

        try:
            if self._rotate_if_needed(self.legacy_history_path, self.max_legacy_bytes):
                rotations += 1
            with self.legacy_history_path.open("a", encoding="utf-8") as handle:
                handle.write(serialized)
        except Exception:
            pass

        state = self._read_state()
        state["record_count"] = int(state.get("record_count", 0)) + 1
        state["rotation_count"] = int(state.get("rotation_count", 0)) + rotations
        state["last_record_timestamp"] = record.get("timestamp")
        state["history_path"] = str(self.history_path)
        state["legacy_history_path"] = str(self.legacy_history_path)
        self._write_state(state)
        return state

    def record(
        self,
        payload: dict[str, Any] | None = None,
        primitive: str | None = None,
        validation_status: str | bool | None = None,
        governance_status: str | bool | None = None,
        runtime_status: str | bool | None = None,
    ) -> dict[str, Any]:
        record = self.normalize(
            payload=payload,
            primitive=primitive,
            validation_status=validation_status,
            governance_status=governance_status,
            runtime_status=runtime_status,
        )
        state = self.append(record)
        return {
            "primitive": PRIMITIVE,
            "recorded": True,
            "history_path": str(self.history_path),
            "legacy_history_path": str(self.legacy_history_path),
            "state_path": str(self.state_path),
            "record": record,
            "record_count": state.get("record_count", 0),
            "metrics_history_exists": self.history_path.exists(),
            "error_count": 0,
        }

    def tail(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        safe_limit = max(1, min(1000, int(limit)))
        lines = self.history_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-safe_limit:]
        records: list[dict[str, Any]] = []
        for line in lines:
            try:
                records.append(json.loads(line))
            except Exception:
                pass
        return records

    def step(self, inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        sample_payload = inputs.get("payload")
        if not isinstance(sample_payload, dict):
            sample_payload = {
                "primitive": inputs.get("primitive", PRIMITIVE),
                "metrics": inputs.get("metrics", {"metrics_history_recorder_self_test": 1.0}),
                "validation_status": inputs.get("validation_status", "validated"),
                "governance_status": inputs.get("governance_status", "governed"),
                "runtime_status": inputs.get("runtime_status", "operational"),
                "error_count": inputs.get("error_count", 0),
            }
        result = self.record(
            sample_payload,
            primitive=inputs.get("primitive"),
            validation_status=inputs.get("validation_status"),
            governance_status=inputs.get("governance_status"),
            runtime_status=inputs.get("runtime_status"),
        )
        recent = self.tail(limit=5)
        result.update({
            "sample_count": len(recent),
            "schema_fields": [
                "timestamp",
                "primitive",
                "metrics",
                "validation_status",
                "governance_status",
                "runtime_status",
                "error_count",
            ],
            "history_directory": str(self.metrics_dir),
            "disk_quota_bytes": self.max_history_bytes,
            "local_disk_usage_bounded": True,
            "e1_metrics_history_core_operational": bool(result.get("metrics_history_exists")),
        })
        return result


ENGINE = MetricsHistoryRecorder()


def record_metrics(payload: dict[str, Any] | None = None, primitive: str | None = None, **status: Any) -> dict[str, Any]:
    """Safe functional helper for runtime hooks."""
    try:
        return MetricsHistoryRecorder().record(payload or {}, primitive=primitive, **status)
    except Exception as exc:
        return {
            "primitive": PRIMITIVE,
            "recorded": False,
            "error": repr(exc),
            "error_count": 1,
        }


def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
