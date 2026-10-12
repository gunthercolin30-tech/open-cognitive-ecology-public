\
"""ACEE3 — governed bridge adapter for heterogeneous evolution-engine outputs.

This primitive never executes source engines. It only normalizes already-produced
results into a deterministic, traceable ACEE contract while preserving raw data.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PRIMITIVE = "ACEE_BRIDGE_ADAPTER"
STATUS_READY = "ACEE_BRIDGE_ADAPTER_READY"
STATUS_DEGRADED = "ACEE_BRIDGE_ADAPTER_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
SUPPORTED_SOURCES = (
    "auto_improvement_runtime_bridge",
    "controlled_evolution_orchestrator",
    "recursive_self_improvement_controller",
    "recursive_self_improvement_governor",
    "evolution_sandbox",
    "runtime_experiment_manager",
)
DEPENDENCIES = [
    "acee_integration_auditor",
    "acee_capability_map",
    "auto_improvement_runtime_bridge",
    "controlled_evolution_orchestrator",
    "recursive_self_improvement_controller",
    "recursive_self_improvement_governor",
    "evolution_sandbox",
    "runtime_experiment_manager",
    "epistemic_guard",
]

SCORE_FIELDS = (
    "pipeline_score",
    "orchestration_stability_index",
    "self_improvement_control_score",
    "sandbox_score",
    "outcome_score",
    "validation_score",
    "global_viability_score",
    "success_rate",
)
CONFIDENCE_FIELDS = (
    "confidence",
    "outcome_confidence",
    "validation_success_rate",
    "governance_approval_rate",
)
RISK_FIELDS = (
    "risk_score",
    "regression_risk",
    "closure_pressure_delta",
    "degradation_rate",
)
STATUS_FIELDS = (
    "status",
    "integration_status",
    "phase",
    "sandbox_decision",
    "decision",
)
ARTIFACT_FIELDS = (
    "report_path",
    "record_path",
    "state_path",
    "history_path",
    "output_path",
    "artifacts",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _bounded(value: Any) -> float | None:
    number = _finite(value)
    if number is None:
        return None
    return round(max(0.0, min(1.0, number)), 6)


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "approved", "accepted", "executed", "completed"}:
            return True
        if lowered in {"false", "no", "rejected", "declined", "failed"}:
            return False
    return None


def _first_mapping(result: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    value = result.get(key)
    return value if isinstance(value, Mapping) else None


def _flatten_candidates(raw: Mapping[str, Any]) -> dict[str, Any]:
    flattened = dict(raw)
    for key in ("diagnostics", "metrics", "final_metrics", "drift_analysis"):
        nested = _first_mapping(raw, key)
        if nested:
            for nested_key, nested_value in nested.items():
                flattened.setdefault(nested_key, nested_value)
    return flattened


def _normalize_status(raw: Mapping[str, Any], source: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    executed = _as_bool(raw.get("executed"))
    accepted = _as_bool(raw.get("accepted"))
    approved = _as_bool(raw.get("approved"))
    sandbox_approved = _as_bool(raw.get("sandbox_approved"))
    rollback_performed = _as_bool(raw.get("rollback_performed"))
    degraded = _as_bool(raw.get("degradation_detected"))
    failed = _as_bool(raw.get("failed"))

    if rollback_performed is True:
        return "rolled_back", warnings
    if failed is True or degraded is True:
        return "degraded", warnings
    if executed is True:
        return "executed", warnings
    if accepted is True or approved is True or sandbox_approved is True:
        return "approved", warnings

    textual = None
    for field in STATUS_FIELDS:
        if raw.get(field) is not None:
            textual = str(raw.get(field)).strip().lower()
            break
    if textual:
        if "rollback" in textual and ("performed" in textual or "rolled" in textual):
            return "rolled_back", warnings
        if any(token in textual for token in ("reject", "declin", "fail", "degrad")):
            return "rejected" if "reject" in textual or "declin" in textual else "degraded", warnings
        if any(token in textual for token in ("execut", "complete", "success")):
            return "executed", warnings
        if any(token in textual for token in ("approv", "accept")):
            return "approved", warnings
        if any(token in textual for token in ("ready", "operational", "idle", "pending")):
            return "ready", warnings
        warnings.append(f"unrecognized_status:{textual}")

    if source == "runtime_experiment_manager" and raw.get("cycles_executed"):
        return "executed", warnings
    return "unknown", warnings


def _pick_numeric(raw: Mapping[str, Any], fields: tuple[str, ...]) -> tuple[float | None, str | None, list[str]]:
    warnings: list[str] = []
    seen: list[tuple[str, float]] = []
    for field in fields:
        if field in raw:
            value = _finite(raw.get(field))
            if value is None:
                warnings.append(f"invalid_numeric:{field}")
            else:
                seen.append((field, value))
    if not seen:
        return None, None, warnings
    selected_field, selected_value = seen[0]
    if len({round(value, 12) for _, value in seen}) > 1:
        warnings.append("multiple_numeric_candidates")
    return round(max(0.0, min(1.0, selected_value)), 6), selected_field, warnings


def _normalize_artifacts(raw: Mapping[str, Any]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for field in ARTIFACT_FIELDS:
        value = raw.get(field)
        if value is None:
            continue
        if field == "artifacts" and isinstance(value, list):
            for item in value:
                artifacts.append({"source_field": field, "value": deepcopy(item)})
        else:
            artifacts.append({"source_field": field, "value": deepcopy(value)})
    return artifacts


@dataclass
class AceeBridgeAdapter:
    root: Path | None = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def _paths(self) -> tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE3_acee_bridge_adapter"
        return (
            directory / "latest_normalized_result.json",
            directory / "normalized_result_history.jsonl",
            directory / ".bridge_adapter.lock",
        )

    def _read_previous(self, history_path: Path) -> tuple[dict[str, Any] | None, bool]:
        if not history_path.is_file():
            return None, False
        try:
            lines = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            return (json.loads(lines[-1]), False) if lines else (None, False)
        except (OSError, json.JSONDecodeError):
            return None, True

    def _build(self, supplied: Mapping[str, Any], previous_hash: str | None, history_corrupted: bool) -> dict[str, Any]:
        source = str(supplied.get("source_module") or supplied.get("source_primitive") or "").strip().lower()
        source = source.removeprefix("ontology.") if hasattr(str, "removeprefix") else (source[9:] if source.startswith("ontology.") else source)
        raw_value = supplied.get("source_result")
        raw = dict(raw_value) if isinstance(raw_value, Mapping) else {}
        flattened = _flatten_candidates(raw)
        degraded_reasons: list[str] = []
        warnings: list[str] = []

        if not source:
            degraded_reasons.append("missing_source_module")
        elif source not in SUPPORTED_SOURCES:
            degraded_reasons.append("unsupported_source_module")
        if not isinstance(raw_value, Mapping):
            degraded_reasons.append("source_result_not_mapping")
        if not raw:
            degraded_reasons.append("empty_source_result")
        if history_corrupted:
            degraded_reasons.append("history_corrupted")

        status, status_warnings = _normalize_status(flattened, source)
        warnings.extend(status_warnings)
        score, score_field, score_warnings = _pick_numeric(flattened, SCORE_FIELDS)
        confidence, confidence_field, confidence_warnings = _pick_numeric(flattened, CONFIDENCE_FIELDS)
        warnings.extend(score_warnings)
        warnings.extend(confidence_warnings)

        risk, risk_field, risk_warnings = _pick_numeric(flattened, RISK_FIELDS)
        warnings.extend(risk_warnings)
        if risk_field == "closure_pressure_delta" and risk is not None:
            risk = round(max(0.0, min(1.0, risk)), 6)

        accepted = next((value for value in (_as_bool(flattened.get(key)) for key in ("accepted", "approved", "sandbox_approved")) if value is not None), None)
        executed = _as_bool(flattened.get("executed"))
        if executed is None and source == "runtime_experiment_manager":
            executed = status == "executed"

        rollback_available = next((value for value in (_as_bool(flattened.get(key)) for key in ("rollback_available", "rollback_functional", "auto_rollback")) if value is not None), None)
        rollback_required = next((value for value in (_as_bool(flattened.get(key)) for key in ("rollback_required", "sandbox_rollback_required")) if value is not None), None)
        rollback_performed = _as_bool(flattened.get("rollback_performed"))
        if rollback_performed is True and rollback_available is False:
            warnings.append("rollback_performed_but_marked_unavailable")
        if accepted is True and executed is False:
            warnings.append("approved_not_executed")

        recommendation = flattened.get("recommendation") or flattened.get("recommended_action") or flattened.get("next_action")
        reason = flattened.get("reason") or flattened.get("decision_reason") or flattened.get("sandbox_decision")
        metrics = deepcopy(raw.get("metrics")) if isinstance(raw.get("metrics"), Mapping) else {}
        diagnostics = deepcopy(raw.get("diagnostics")) if isinstance(raw.get("diagnostics"), Mapping) else {}

        required = ("source_module", "source_result")
        missing_fields = [field for field in required if not supplied.get(field)]
        normalization_complete = not degraded_reasons and status != "unknown"
        if score is None:
            warnings.append("score_unavailable")
        if confidence is None:
            warnings.append("confidence_unavailable")
        normalization_confidence = round(max(0.0, 1.0 - (0.12 * len(set(warnings))) - (0.25 * len(degraded_reasons))), 6)

        timestamp = str(supplied.get("adapter_timestamp_utc") or _utc_now())
        source_schema = sorted(str(key) for key in raw.keys())
        source_result_hash = _sha256(raw)
        payload = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "adapter_timestamp_utc": timestamp,
            "source_module": source,
            "source_primitive": raw.get("primitive"),
            "source_schema": source_schema,
            "source_result_hash": source_result_hash,
            "raw_result": deepcopy(raw),
            "status": status,
            "accepted": accepted,
            "executed": executed,
            "score": score,
            "score_source_field": score_field,
            "confidence": confidence,
            "confidence_source_field": confidence_field,
            "risk_score": risk,
            "risk_source_field": risk_field,
            "recommendation": deepcopy(recommendation),
            "reason": deepcopy(reason),
            "rollback_available": rollback_available,
            "rollback_required": rollback_required,
            "rollback_performed": rollback_performed,
            "artifacts": _normalize_artifacts(raw),
            "metrics": metrics,
            "diagnostics": diagnostics,
            "missing_fields": sorted(set(missing_fields)),
            "normalization_warnings": sorted(set(warnings)),
            "normalization_complete": normalization_complete,
            "normalization_confidence": normalization_confidence,
            "degraded_reasons": sorted(set(degraded_reasons)),
            "previous_normalized_hash": previous_hash,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        normalized_hash = _sha256(payload)
        adapter_ready = normalization_complete
        payload.update({
            "adapter_status": STATUS_READY if adapter_ready else STATUS_DEGRADED,
            "adapter_ready": adapter_ready,
            "adapter_id": f"ACEE3-{normalized_hash[:16]}",
            "normalized_hash": normalized_hash,
        })
        return payload

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        supplied = dict(inputs or {})
        latest_path, history_path, lock_path = self._paths()

        if persist:
            latest_path.parent.mkdir(parents=True, exist_ok=True)
            with lock_path.open("a+", encoding="utf-8") as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                previous, corrupted = self._read_previous(history_path)
                result = self._build(supplied, previous.get("normalized_hash") if previous else None, corrupted)
                result["persisted"] = True
                result["output_path"] = str(latest_path)
                result["history_path"] = str(history_path)
                latest_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
                with history_path.open("a", encoding="utf-8") as history_file:
                    history_file.write(_canonical(result) + "\n")
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                return result

        previous, corrupted = self._read_previous(history_path)
        result = self._build(supplied, previous.get("normalized_hash") if previous else None, corrupted)
        result["persisted"] = False
        result["output_path"] = str(latest_path)
        result["history_path"] = str(history_path)
        return result
