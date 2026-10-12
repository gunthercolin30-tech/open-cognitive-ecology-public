"""ACEE2 — passive governed meta-orchestration facade.

This primitive coordinates public results from ACEE0, ACEE1 and ACEE3. It never
executes a source engine, dispatches an action, installs code, or bypasses a gate.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_META_ORCHESTRATOR"
STATUS_READY = "ACEE_META_ORCHESTRATOR_READY"
STATUS_DEGRADED = "ACEE_META_ORCHESTRATOR_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "approved", "accepted", "authorized", "passed"}:
            return True
        if lowered in {"false", "no", "rejected", "declined", "blocked", "failed"}:
            return False
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    return None


def _decision(raw: Mapping[str, Any], keys: Tuple[str, ...]) -> Optional[bool]:
    for key in keys:
        if key in raw:
            parsed = _bool(raw.get(key))
            if parsed is not None:
                return parsed
    status = str(raw.get("status") or raw.get("decision") or "").lower()
    if any(token in status for token in ("reject", "declin", "block", "fail")):
        return False
    if any(token in status for token in ("approv", "accept", "authoriz", "pass")):
        return True
    return None


def _select_capability(capability_map: Mapping[str, Any]) -> Tuple[Optional[str], Optional[str], List[str]]:
    matrix = capability_map.get("capability_matrix")
    if not isinstance(matrix, Mapping):
        return None, None, ["capability_matrix_missing"]
    candidates = []
    for stage, entry in matrix.items():
        if not isinstance(entry, Mapping):
            continue
        level = str(entry.get("coverage_level") or "unknown")
        if level == "deferred":
            continue
        action = str(entry.get("recommended_action") or "")
        score = entry.get("coverage_score")
        try:
            numeric = float(score)
        except (TypeError, ValueError):
            numeric = 1.0
        priority = {"missing": 0, "weakly_covered": 1, "partially_covered": 2, "substantially_covered": 3, "covered": 4}.get(level, 5)
        candidates.append((priority, numeric, str(stage), action))
    if not candidates:
        return None, None, ["no_non_deferred_capability"]
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    _, _, stage, action = candidates[0]
    return stage, action or None, []


def _select_engine(selected_capability: Optional[str], capability_map: Mapping[str, Any], normalized: Mapping[str, Any]) -> Tuple[Optional[str], str, List[str]]:
    matrix = capability_map.get("capability_matrix")
    entry = matrix.get(selected_capability) if isinstance(matrix, Mapping) and selected_capability else None
    warnings = []
    if isinstance(entry, Mapping):
        primary = entry.get("primary_module")
        if isinstance(primary, str) and primary.strip():
            return primary.strip(), "capability_map_primary_module", warnings
        modules = entry.get("candidate_modules")
        if isinstance(modules, list):
            valid = sorted(str(item) for item in modules if str(item).strip())
            if valid:
                return valid[0], "capability_map_candidate_module", warnings
    source = normalized.get("source_module")
    if isinstance(source, str) and source.strip():
        warnings.append("engine_selected_from_normalized_source")
        return source.strip(), "normalized_result_source_module", warnings
    return None, "no_compatible_engine", ["compatible_engine_missing"]


@dataclass
class AceeMetaOrchestrator:
    root: Optional[Path] = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def _paths(self) -> Tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE2_acee_meta_orchestrator"
        return directory / "latest_orchestration_cycle.json", directory / "orchestration_cycle_history.jsonl", directory / ".meta_orchestrator.lock"

    def _previous(self, history_path: Path) -> Tuple[Optional[Dict[str, Any]], bool]:
        if not history_path.is_file():
            return None, False
        try:
            lines = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            return (json.loads(lines[-1]), False) if lines else (None, False)
        except (OSError, json.JSONDecodeError):
            return None, True

    def _build(self, supplied: Mapping[str, Any], previous_hash: Optional[str], history_corrupted: bool) -> Dict[str, Any]:
        audit = _mapping(supplied.get("integration_audit"))
        capability_map = _mapping(supplied.get("capability_map"))
        normalized = _mapping(supplied.get("normalized_engine_result"))
        governor = _mapping(supplied.get("governor_decision"))
        constitutional = _mapping(supplied.get("constitutional_decision"))
        human = _mapping(supplied.get("human_review"))
        blocking = []
        warnings = []

        if audit.get("audit_completed") is not True or audit.get("audit_status") != "ACEE_INTEGRATION_AUDIT_COMPLETE":
            blocking.append("integration_audit_unavailable_or_degraded")
        if capability_map.get("capability_map_ready") is not True or capability_map.get("capability_map_status") != "ACEE_CAPABILITY_MAP_READY":
            blocking.append("capability_map_unavailable_or_degraded")
        if normalized.get("adapter_ready") is not True or normalized.get("adapter_status") != "ACEE_BRIDGE_ADAPTER_READY":
            blocking.append("normalized_engine_result_unavailable_or_degraded")

        selected_capability, recommended_action, selection_warnings = _select_capability(capability_map)
        warnings.extend(selection_warnings)
        selected_engine, engine_reason, engine_warnings = _select_engine(selected_capability, capability_map, normalized)
        warnings.extend(engine_warnings)
        if selected_capability is None:
            blocking.append("selected_capability_missing")
        if selected_engine is None:
            blocking.append("selected_engine_missing")

        matrix = capability_map.get("capability_matrix")
        selected_entry = matrix.get(selected_capability, {}) if isinstance(matrix, Mapping) and selected_capability else {}
        coverage_level = str(selected_entry.get("coverage_level") or "unknown") if isinstance(selected_entry, Mapping) else "unknown"
        if coverage_level == "deferred":
            blocking.append("selected_capability_deferred")
        if coverage_level == "missing" and not selected_engine:
            blocking.append("missing_capability_without_engine")

        governor_ok = _decision(governor, ("approved", "authorized", "accepted", "governance_approved"))
        constitutional_ok = _decision(constitutional, ("approved", "authorized", "accepted", "constitutional_compliant"))
        human_required = _bool(supplied.get("human_review_required"))
        if human_required is None:
            human_required = _bool(human.get("required")) or False
        human_ok = _decision(human, ("approved", "authorized", "accepted", "review_approved"))

        if governor_ok is False:
            blocking.append("governor_rejected")
        elif governor_ok is None:
            blocking.append("governor_decision_missing")
        if constitutional_ok is False:
            blocking.append("constitutional_gate_rejected")
        elif constitutional_ok is None:
            blocking.append("constitutional_decision_missing")
        if human_required and human_ok is not True:
            blocking.append("human_review_required_not_approved")

        normalized_status = str(normalized.get("status") or "unknown")
        rollback_available = bool(normalized.get("rollback_available") is True)
        rollback_required = bool(normalized.get("rollback_required") is True or normalized_status == "rolled_back")
        rollback_reason = "normalized_engine_result_requires_rollback" if rollback_required else None
        if rollback_required:
            blocking.append("rollback_required")

        execution_eligible = not blocking and governor_ok is True and constitutional_ok is True and (not human_required or human_ok is True)
        execution_authorized = execution_eligible
        execution_dispatched = False

        if "governor_rejected" in blocking:
            cycle_status = "governance_rejected"
        elif "constitutional_gate_rejected" in blocking:
            cycle_status = "execution_blocked"
        elif "human_review_required_not_approved" in blocking:
            cycle_status = "human_review_required"
        elif rollback_required:
            cycle_status = "rollback_required"
        elif execution_eligible:
            cycle_status = "execution_eligible"
        elif blocking:
            cycle_status = "degraded"
        else:
            cycle_status = "cycle_complete"

        next_action = "prepare_governed_execution_request" if execution_eligible else "resolve_blocking_reasons"
        if rollback_required:
            next_action = "request_governed_rollback"
        elif human_required and human_ok is not True:
            next_action = "request_human_review"

        timestamp = str(supplied.get("cycle_timestamp_utc") or _utc_now())
        trace = [
            {"step": 1, "name": "integration_audit", "passed": "integration_audit_unavailable_or_degraded" not in blocking},
            {"step": 2, "name": "capability_selection", "selected": selected_capability, "coverage_level": coverage_level},
            {"step": 3, "name": "engine_selection", "selected": selected_engine, "reason": engine_reason},
            {"step": 4, "name": "normalized_result", "status": normalized_status},
            {"step": 5, "name": "governance", "decision": governor_ok},
            {"step": 6, "name": "constitutional_gate", "decision": constitutional_ok},
            {"step": 7, "name": "human_review", "required": human_required, "decision": human_ok},
            {"step": 8, "name": "execution_eligibility", "eligible": execution_eligible, "dispatched": False},
        ]
        payload = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "cycle_timestamp_utc": timestamp,
            "source_audit_hash": audit.get("audit_hash"),
            "source_mapping_hash": capability_map.get("mapping_hash"),
            "source_normalized_hash": normalized.get("normalized_hash"),
            "selected_capability": selected_capability,
            "capability_coverage_level": coverage_level,
            "selected_engine": selected_engine,
            "engine_selection_reason": engine_reason,
            "governor_decision": governor_ok,
            "constitutional_decision": constitutional_ok,
            "human_review_required": human_required,
            "human_review_status": human_ok,
            "execution_eligible": execution_eligible,
            "execution_authorized": execution_authorized,
            "execution_dispatched": False,
            "rollback_available": rollback_available,
            "rollback_required": rollback_required,
            "blocking_reasons": sorted(set(blocking)),
            "warnings": sorted(set(warnings)),
            "next_action": next_action,
            "orchestration_trace": trace,
            "previous_trace_hash": previous_hash,
        }
        trace_hash = _sha256(payload)
        cycle_id = "acee2-" + trace_hash[:16]
        ready = len(payload["blocking_reasons"]) == 0 or cycle_status in {"execution_eligible", "human_review_required", "governance_rejected", "execution_blocked", "rollback_required"}
        result = {
            **payload,
            "cycle_id": cycle_id,
            "cycle_status": cycle_status,
            "cycle_complete": True,
            "source_audit_id": audit.get("audit_id"),
            "selected_capability_recommended_action": recommended_action,
            "normalized_engine_result": deepcopy(normalized),
            "normalized_engine_status": normalized_status,
            "rollback_reason": rollback_reason,
            "decision_count": 3,
            "trace_hash": trace_hash,
            "orchestrator_status": STATUS_READY if ready and not history_corrupted else STATUS_DEGRADED,
            "orchestrator_ready": bool(ready and not history_corrupted),
            "history_corrupted": history_corrupted,
            "persisted": False,
            "output_path": None,
            "history_path": None,
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
        return result

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        supplied = dict(inputs) if isinstance(inputs, Mapping) else {}
        latest_path, history_path, lock_path = self._paths()
        if not persist:
            previous, corrupted = self._previous(history_path)
            previous_hash = previous.get("trace_hash") if isinstance(previous, Mapping) else None
            return self._build(supplied, previous_hash, corrupted)
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+", encoding="utf-8") as lock_handle:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
            previous, corrupted = self._previous(history_path)
            previous_hash = previous.get("trace_hash") if isinstance(previous, Mapping) else None
            result = self._build(supplied, previous_hash, corrupted)
            latest_path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(_canonical(result) + "\n")
            result["persisted"] = True
            result["output_path"] = str(latest_path)
            result["history_path"] = str(history_path)
            latest_path.write_text(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return result
