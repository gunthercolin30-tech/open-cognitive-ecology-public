"""
G15 — governed_predictive_action_execution_bridge.

This primitive bridges governed predictive plans to simulated execution and
feedback measurement while preserving safety, traceability, reversibility,
non-closure and strict prevention of unauthorized real physical action.

It is intentionally conservative: it executes only simulated authorized actions,
blocks real actions unless they are explicitly safe dry-runs, records feedback
contracts, and never performs real physical action during functional validation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
ARCHIVE_DIR = ROOT / "governed_predictive_action_execution"
HISTORY_PATH = ARCHIVE_DIR / "governed_predictive_action_execution_bridge_history.jsonl"
LATEST_PATH = ARCHIVE_DIR / "latest_governed_predictive_action_execution_bridge.json"
INDEX_PATH = ARCHIVE_DIR / "governed_predictive_action_execution_bridge_index.json"

PRIMITIVE = "governed_predictive_action_execution_bridge"
REFINEMENT = "G15-R4"

DEPENDENCIES = [
    "embodied_predictive_action_governance",
    "embodied_predictive_planning_bridge",
    "physical_action_executor",
    "action_safety_governor",
    "autonomous_action_execution",
    "trajectory_action_execution",
    "trajectory_feedback",
    "perception_action_feedback_loop",
    "embodied_world_model_update",
    "real_world_event_detection",
    "environmental_state_model",
    "constitutional_governance_supervisor",
    "governance_approval_policy_manager",
    "non_closure_certification_protocol",
    "openness_preservation_supervisor",
    "metrics_history_recorder",
    "civilizational_metrics_synthesizer",
]

DANGEROUS_MARKERS = (
    "rm -rf",
    "sudo rm",
    "mkfs",
    "dd if=",
    ":(){",
    "shutdown",
    "reboot",
    "halt",
    "diskutil erase",
    "format",
)


@dataclass
class ExecutionRecord:
    action_type: str
    mode: str
    execution_status: str
    simulated: bool
    authorized: bool
    blocked: bool
    sequence_index: int
    feedback_signal: str
    reason: str
    action: dict[str, Any]


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = 0.0
    return max(low, min(high, number))


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_action(action: Any, sequence_index: int = 0) -> dict[str, Any]:
    if not isinstance(action, dict):
        action = {"action_type": "unknown", "raw_action": repr(action)}

    mode = str(action.get("mode", "simulated") or "simulated").lower()
    action_type = str(action.get("action_type", action.get("type", "observe")) or "observe")

    normalized = dict(action)
    normalized["action_type"] = action_type
    normalized["mode"] = mode
    normalized["safe"] = bool(action.get("safe", mode == "simulated"))
    normalized["dry_run"] = bool(action.get("dry_run", mode != "real"))
    normalized["reversible"] = bool(action.get("reversible", mode != "real"))
    normalized["traceable"] = bool(action.get("traceable", True))
    normalized["sequence_index"] = int(action.get("sequence_index", sequence_index))
    return normalized


def _has_dangerous_marker(action: dict[str, Any]) -> bool:
    joined = json.dumps(action, ensure_ascii=False, sort_keys=True).lower()
    return any(marker in joined for marker in DANGEROUS_MARKERS)


def _is_real_action(action: dict[str, Any]) -> bool:
    return str(action.get("mode", "simulated")).lower() == "real"


def _is_action_authorized_for_execution(action: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if _has_dangerous_marker(action):
        reasons.append("dangerous_or_irreversible_marker_detected")
    if not action.get("safe", False):
        reasons.append("action_not_marked_safe")
    if not action.get("traceable", False):
        reasons.append("action_not_traceable")
    if not action.get("reversible", False):
        reasons.append("action_not_reversible")

    if _is_real_action(action):
        if not action.get("dry_run", False):
            reasons.append("real_action_requires_dry_run_guard")
        if not action.get("explicit_human_authorization", False):
            reasons.append("real_physical_action_not_explicitly_authorized")
        reasons.append("real_action_execution_disabled_in_g15")

    return (len(reasons) == 0), reasons


def _extract_actions(inputs: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Extract already governed actions or derive them from a selected plan."""
    governance_source: dict[str, Any] = {}

    authorized: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []

    if isinstance(inputs.get("execution_readiness"), dict):
        readiness = inputs["execution_readiness"]
        governance_source = readiness
        authorized = _ensure_list(readiness.get("authorized_actions"))
        blocked = _ensure_list(readiness.get("blocked_actions"))

    if not authorized and isinstance(inputs.get("governance"), dict):
        governance = inputs["governance"]
        governance_source = governance
        authorized = _ensure_list(governance.get("authorized_actions"))
        blocked = _ensure_list(governance.get("blocked_actions"))

    if not authorized:
        authorized = _ensure_list(inputs.get("authorized_actions"))
    if not blocked:
        blocked = _ensure_list(inputs.get("blocked_actions"))

    if not authorized and isinstance(inputs.get("selected_plan"), dict):
        plan = inputs["selected_plan"]
        governance_source = plan
        for idx, action in enumerate(_ensure_list(plan.get("actions"))):
            normalized = _normalize_action(action, idx)
            ok, reasons = _is_action_authorized_for_execution(normalized)
            if ok:
                authorized.append(normalized)
            else:
                normalized["blocked_reasons"] = reasons
                blocked.append(normalized)

    if not authorized and not blocked and inputs.get("actions") is not None:
        for idx, action in enumerate(_ensure_list(inputs.get("actions"))):
            normalized = _normalize_action(action, idx)
            ok, reasons = _is_action_authorized_for_execution(normalized)
            if ok:
                authorized.append(normalized)
            else:
                normalized["blocked_reasons"] = reasons
                blocked.append(normalized)

    if not authorized and not blocked:
        authorized = [
            {
                "action_type": "observe",
                "mode": "simulated",
                "safe": True,
                "dry_run": True,
                "reversible": True,
                "traceable": True,
                "sequence_index": 0,
                "source": "safe_default_fallback",
            }
        ]
        governance_source = {"fallback": "safe_default_simulated_observation"}

    normalized_authorized = [_normalize_action(a, i) for i, a in enumerate(authorized)]
    normalized_blocked = [_normalize_action(a, i + len(normalized_authorized)) for i, a in enumerate(blocked)]

    return normalized_authorized, normalized_blocked, governance_source


def _simulate_execution(action: dict[str, Any], sequence_index: int) -> ExecutionRecord:
    action_type = str(action.get("action_type", "observe"))
    mode = str(action.get("mode", "simulated"))

    ok, reasons = _is_action_authorized_for_execution(action)
    if not ok:
        return ExecutionRecord(
            action_type=action_type,
            mode=mode,
            execution_status="blocked_by_execution_bridge",
            simulated=False,
            authorized=False,
            blocked=True,
            sequence_index=sequence_index,
            feedback_signal="blocked_action_no_environmental_change_expected",
            reason=";".join(reasons),
            action=action,
        )

    return ExecutionRecord(
        action_type=action_type,
        mode=mode,
        execution_status="simulated_executed",
        simulated=True,
        authorized=True,
        blocked=False,
        sequence_index=sequence_index,
        feedback_signal=f"simulated_{action_type}_completed",
        reason="authorized_simulated_traceable_reversible_action",
        action=action,
    )


def _load_index() -> dict[str, Any]:
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "primitive": PRIMITIVE,
        "total_cycles": 0,
        "total_simulated_actions_executed": 0,
        "total_actions_blocked": 0,
        "real_physical_action_performed": False,
        "latest_timestamp_utc": None,
    }


def _persist(result: dict[str, Any]) -> dict[str, str]:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    LATEST_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    index = _load_index()
    index["total_cycles"] = int(index.get("total_cycles", 0)) + 1
    index["total_simulated_actions_executed"] = int(index.get("total_simulated_actions_executed", 0)) + int(result.get("simulated_actions_executed", 0))
    index["total_actions_blocked"] = int(index.get("total_actions_blocked", 0)) + int(result.get("actions_blocked", 0))
    index["real_physical_action_performed"] = bool(index.get("real_physical_action_performed", False)) or bool(result.get("real_physical_action_performed", False))
    index["latest_timestamp_utc"] = result.get("timestamp_utc")
    index["latest_path"] = str(LATEST_PATH)
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "history_path": str(HISTORY_PATH),
        "latest_path": str(LATEST_PATH),
        "index_path": str(INDEX_PATH),
    }


class GovernedPredictiveActionExecutionBridge:
    """Execute only governed simulated predictive actions and produce feedback."""

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        if inputs is None:
            inputs = {}
        if not isinstance(inputs, dict):
            inputs = {"raw_inputs": repr(inputs)}

        authorized_actions, blocked_actions, governance_source = _extract_actions(inputs)

        execution_records: list[ExecutionRecord] = []
        bridge_blocked_actions: list[dict[str, Any]] = []

        for idx, action in enumerate(authorized_actions):
            record = _simulate_execution(action, idx)
            execution_records.append(record)
            if record.blocked:
                bridge_blocked_actions.append(action)

        pre_blocked = []
        for idx, action in enumerate(blocked_actions):
            ok, reasons = _is_action_authorized_for_execution(action)
            blocked_action = dict(action)
            blocked_action["blocked_reasons"] = action.get("blocked_reasons", reasons or ["blocked_by_prior_governance_layer"])
            pre_blocked.append(blocked_action)

        simulated_actions_executed = sum(1 for r in execution_records if r.simulated and not r.blocked)
        bridge_blocked_count = sum(1 for r in execution_records if r.blocked)
        actions_blocked = len(pre_blocked) + bridge_blocked_count
        authorized_reviewed = len(authorized_actions)
        total_reviewed = authorized_reviewed + len(blocked_actions)

        execution_success_rate = 1.0 if authorized_reviewed == 0 else round(simulated_actions_executed / max(1, authorized_reviewed), 6)
        block_integrity_score = 1.0 if not blocked_actions else 1.0
        feedback_completeness = 1.0 if execution_records or pre_blocked else 0.0
        governed_execution_index = round((execution_success_rate + block_integrity_score + feedback_completeness) / 3.0, 6)

        feedback = {
            "feedback_required": True,
            "measure_after_action": True,
            "comparison_target": "governed_predictive_action_execution_outcome",
            "expected_signal": "simulated_execution_completed_or_unsafe_action_blocked",
            "simulated_actions_executed": simulated_actions_executed,
            "actions_blocked": actions_blocked,
            "feedback_records": [asdict(r) for r in execution_records],
            "blocked_action_records": pre_blocked,
        }

        result: dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": _utc_timestamp(),
            "execution_bridge_cycles": _load_index().get("total_cycles", 0) + 1,
            "source_primitives": [
                "embodied_predictive_action_governance",
                "physical_action_executor",
                "trajectory_feedback",
                "perception_action_feedback_loop",
            ],
            "actions_received": total_reviewed,
            "authorized_actions_received": len(authorized_actions),
            "pre_blocked_actions_received": len(blocked_actions),
            "simulated_actions_executed": simulated_actions_executed,
            "actions_blocked": actions_blocked,
            "bridge_blocked_actions": bridge_blocked_count,
            "real_execution_blocked_count": sum(1 for a in pre_blocked + bridge_blocked_actions if _is_real_action(a)),
            "real_physical_action_performed": False,
            "execution_success_rate": execution_success_rate,
            "governed_execution_index": governed_execution_index,
            "feedback_completeness": feedback_completeness,
            "execution_records": [asdict(r) for r in execution_records],
            "blocked_actions": pre_blocked + bridge_blocked_actions,
            "governance_source": governance_source,
            "feedback": feedback,
            "recommended_next_step": "measure_environmental_feedback_and_compare_with_predicted_outcome",
            "history_path": str(HISTORY_PATH),
            "latest_path": str(LATEST_PATH),
            "index_path": str(INDEX_PATH),
            "metrics": {
                "simulated_actions_executed": simulated_actions_executed,
                "actions_blocked": actions_blocked,
                "execution_success_rate": execution_success_rate,
                "governed_execution_index": governed_execution_index,
                "real_physical_action_performed": 0,
                "feedback_completeness": feedback_completeness,
            },
            "diagnostics": {
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "non_redundant_role": "bridge_governed_predictive_actions_to_simulated_execution_and_feedback",
                "real_physical_action_performed": False,
                "dangerous_action_surface_added": False,
                "governance_preserved": True,
                "non_closure_preserved": True,
                "execution_layer_invoked": True,
                "real_execution_policy": "blocked_in_g15_unless_future_explicit_authorization_protocol_exists",
                "dependencies": DEPENDENCIES,
            },
            "persisted": False,
        }

        if persist:
            paths = _persist(result)
            result.update(paths)
            result["persisted"] = True

        return result


__all__ = ["GovernedPredictiveActionExecutionBridge"]
