# -*- coding: utf-8 -*-
"""
G16 — closed_embodied_feedback_validation_loop.

Closed embodied feedback validation loop.

This primitive validates the complete embodied loop:
observation -> world model -> prediction -> planning -> governance ->
simulated execution -> feedback -> validation -> adaptive correction.

It does not perform real physical action. It validates functional feedback
alignment and records traceable longitudinal metrics.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
ARCHIVE_DIR = ROOT / "closed_embodied_feedback_validation"
HISTORY_PATH = ARCHIVE_DIR / "closed_embodied_feedback_validation_loop_history.jsonl"
LATEST_PATH = ARCHIVE_DIR / "latest_closed_embodied_feedback_validation_loop.json"
INDEX_PATH = ARCHIVE_DIR / "closed_embodied_feedback_validation_loop_index.json"

PRIMITIVE = "closed_embodied_feedback_validation_loop"
REFINEMENT = "G16-R1"

DEPENDENCIES = [
    "perception_action_feedback_loop",
    "governed_predictive_action_execution_bridge",
    "embodied_predictive_action_governance",
    "embodied_predictive_planning_bridge",
    "embodied_world_model_update",
    "world_model_execution_loop",
    "experience_integration_loop",
    "trajectory_feedback",
    "environmental_state_model",
    "real_world_event_detection",
    "physical_environment_alert_router",
    "embodied_environmental_memory_integration",
    "action_safety_governor",
    "physical_action_executor",
    "metrics_history_recorder",
    "civilizational_metrics_synthesizer",
    "scientific_anomaly_detector",
    "constraint_monitoring_system",
]

def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _clamp(value: Any, low: float = 0.0, high: float = 1.0, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = default
    return max(low, min(high, x))

def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]

def _load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

def _append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

def _flatten_action_sources(inputs: dict[str, Any]) -> dict[str, Any]:
    execution = _as_dict(inputs.get("execution_result") or inputs.get("governed_execution"))
    governance = _as_dict(inputs.get("governance_result") or inputs.get("predictive_action_governance"))
    planning = _as_dict(inputs.get("planning_result") or inputs.get("predictive_planning"))

    if not execution and ("simulated_actions_executed" in inputs or "actions_blocked" in inputs):
        execution = inputs

    return {
        "execution": execution,
        "governance": governance,
        "planning": planning,
    }

def _derive_default_inputs() -> dict[str, Any]:
    return {
        "execution_result": {
            "success": True,
            "simulated_actions_executed": 1,
            "actions_blocked": 0,
            "execution_success_rate": 1.0,
            "real_physical_action_performed": False,
            "feedback": {
                "feedback_required": True,
                "measure_after_action": True,
                "expected_signal": "safe_simulated_execution_completed",
            },
        },
        "pre_observation": {
            "vision": {"detected_objects": ["reference_object"]},
            "sensors": {"light": 0.4},
            "runtime": {"storage_online": True},
        },
        "post_observation": {
            "vision": {"detected_objects": ["reference_object"]},
            "sensors": {"light": 0.42},
            "runtime": {"storage_online": True},
        },
        "expected_feedback": {
            "expected_signal": "safe_simulated_execution_completed",
            "target_alignment": 0.9,
        },
    }

def _numeric_delta_score(previous: dict[str, Any], current: dict[str, Any]) -> float:
    deltas: list[float] = []
    for section in ("sensors", "runtime"):
        p = _as_dict(previous.get(section))
        c = _as_dict(current.get(section))
        keys = set(p) | set(c)
        for key in keys:
            pv = p.get(key)
            cv = c.get(key)
            if isinstance(pv, (int, float)) and isinstance(cv, (int, float)):
                deltas.append(min(1.0, abs(float(cv) - float(pv))))
            elif pv != cv:
                deltas.append(0.5)
    pv = set(_as_dict(previous.get("vision")).get("detected_objects", []) or [])
    cv = set(_as_dict(current.get("vision")).get("detected_objects", []) or [])
    if pv or cv:
        overlap = len(pv & cv) / max(1, len(pv | cv))
        deltas.append(1.0 - overlap)
    if not deltas:
        return 0.0
    return _clamp(mean(deltas))

def _alignment_from_observations(previous: dict[str, Any], current: dict[str, Any], target: float) -> float:
    delta = _numeric_delta_score(previous, current)
    stability = 1.0 - min(1.0, delta)
    return _clamp(0.65 * stability + 0.35 * _clamp(target, default=0.8))

def _correction_recommendations(validation_gap: float, blocked: int, real_performed: bool) -> list[str]:
    recommendations: list[str] = []
    if real_performed:
        recommendations.append("halt_and_review_real_physical_action_path")
    if blocked:
        recommendations.append("preserve_blocked_action_trace_for_governance_review")
    if validation_gap > 0.15:
        recommendations.append("increase_observation_after_action_and_reduce_execution_scope")
    if validation_gap > 0.30:
        recommendations.append("trigger_predictive_model_recalibration")
    if not recommendations:
        recommendations.append("reinforce_current_closed_embodied_loop_policy")
    return recommendations

class ClosedEmbodiedFeedbackValidationLoop:
    primitive = PRIMITIVE
    refinement = REFINEMENT
    dependencies = DEPENDENCIES

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.archive_dir = self.root / "closed_embodied_feedback_validation"
        self.history_path = self.archive_dir / "closed_embodied_feedback_validation_loop_history.jsonl"
        self.latest_path = self.archive_dir / "latest_closed_embodied_feedback_validation_loop.json"
        self.index_path = self.archive_dir / "closed_embodied_feedback_validation_loop_index.json"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = _as_dict(inputs)
        if not payload:
            payload = _derive_default_inputs()

        sources = _flatten_action_sources(payload)
        execution = _as_dict(sources["execution"])
        governance = _as_dict(sources["governance"])
        planning = _as_dict(sources["planning"])

        pre = _as_dict(payload.get("pre_observation") or payload.get("previous_observation"))
        post = _as_dict(payload.get("post_observation") or payload.get("current_observation"))
        expected_feedback = _as_dict(payload.get("expected_feedback") or execution.get("feedback"))

        simulated_executed = int(execution.get("simulated_actions_executed", execution.get("executed_action_count", 0)) or 0)
        actions_blocked = int(execution.get("actions_blocked", 0) or 0)
        real_performed = bool(execution.get("real_physical_action_performed", False))
        execution_success_rate = _clamp(execution.get("execution_success_rate", 1.0 if simulated_executed or actions_blocked else 0.75), default=0.75)
        governance_index = _clamp(
            governance.get("predictive_action_governance_index", execution.get("governance_index", 0.9)),
            default=0.9,
        )
        planning_alignment = _clamp(
            planning.get("predicted_outcome_alignment", payload.get("predicted_outcome_alignment", 0.8)),
            default=0.8,
        )
        target_alignment = _clamp(expected_feedback.get("target_alignment", planning_alignment), default=0.8)

        observation_alignment = _alignment_from_observations(pre, post, target_alignment)
        feedback_signal_present = bool(expected_feedback.get("feedback_required", True) or execution.get("feedback"))
        feedback_contract_score = 1.0 if feedback_signal_present else 0.5
        safety_score = 0.0 if real_performed else 1.0
        blocked_trace_score = 1.0 if actions_blocked >= 0 else 0.0

        sensorimotor_alignment_index = _clamp(
            0.40 * observation_alignment
            + 0.25 * execution_success_rate
            + 0.20 * planning_alignment
            + 0.15 * safety_score
        )
        feedback_validation_success_rate = _clamp(
            0.35 * sensorimotor_alignment_index
            + 0.25 * governance_index
            + 0.20 * feedback_contract_score
            + 0.20 * blocked_trace_score
        )
        validation_gap = _clamp(1.0 - feedback_validation_success_rate)
        adaptive_correction_rate = _clamp(validation_gap if validation_gap > 0.05 else 0.0)
        closed_feedback_index = _clamp(
            0.35 * feedback_validation_success_rate
            + 0.25 * sensorimotor_alignment_index
            + 0.20 * execution_success_rate
            + 0.20 * governance_index
        )

        previous_index = _load_json(self.index_path, {})
        cycles = int(previous_index.get("closed_feedback_cycles", 0) or 0) + 1
        cumulative_success = float(previous_index.get("cumulative_feedback_validation_success", 0.0) or 0.0) + feedback_validation_success_rate
        cumulative_corrections = float(previous_index.get("cumulative_adaptive_correction", 0.0) or 0.0) + adaptive_correction_rate

        result = {
            "success": True,
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": _utc(),
            "closed_feedback_cycles": cycles,
            "source_primitives": [
                "perception_action_feedback_loop",
                "governed_predictive_action_execution_bridge",
                "embodied_predictive_action_governance",
                "embodied_predictive_planning_bridge",
                "embodied_world_model_update",
            ],
            "simulated_actions_executed": simulated_executed,
            "actions_blocked": actions_blocked,
            "real_physical_action_performed": real_performed,
            "execution_success_rate": round(execution_success_rate, 6),
            "planning_alignment": round(planning_alignment, 6),
            "governance_index": round(governance_index, 6),
            "observation_alignment": round(observation_alignment, 6),
            "sensorimotor_alignment_index": round(sensorimotor_alignment_index, 6),
            "feedback_validation_success_rate": round(feedback_validation_success_rate, 6),
            "adaptive_correction_rate": round(adaptive_correction_rate, 6),
            "closed_embodied_feedback_index": round(closed_feedback_index, 6),
            "validation_gap": round(validation_gap, 6),
            "feedback": {
                "feedback_required": True,
                "feedback_contract_present": feedback_signal_present,
                "expected_signal": expected_feedback.get("expected_signal", "closed_embodied_feedback_validation"),
                "measure_after_action": bool(expected_feedback.get("measure_after_action", True)),
                "comparison_target": expected_feedback.get("comparison_target", "observed_post_action_state"),
                "validation_status": "validated" if feedback_validation_success_rate >= 0.75 else "requires_adaptive_correction",
            },
            "adaptive_corrections": _correction_recommendations(validation_gap, actions_blocked, real_performed),
            "pre_observation": pre,
            "post_observation": post,
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "index_path": str(self.index_path),
            "metrics": {
                "closed_feedback_cycles": cycles,
                "feedback_validation_success_rate": round(feedback_validation_success_rate, 6),
                "sensorimotor_alignment_index": round(sensorimotor_alignment_index, 6),
                "adaptive_correction_rate": round(adaptive_correction_rate, 6),
                "closed_embodied_feedback_index": round(closed_feedback_index, 6),
                "real_physical_action_performed": int(real_performed),
            },
            "diagnostics": {
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "non_redundant_role": "validate_closed_embodied_feedback_after_governed_simulated_execution",
                "real_physical_action_performed": real_performed,
                "dangerous_action_surface_added": False,
                "governance_preserved": True,
                "non_closure_preserved": True,
                "requires_real_world_authorization_for_real_actions": True,
                "dependencies": DEPENDENCIES,
            },
            "persisted": False,
        }

        index = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "closed_feedback_cycles": cycles,
            "cumulative_feedback_validation_success": cumulative_success,
            "mean_feedback_validation_success_rate": round(cumulative_success / max(1, cycles), 6),
            "cumulative_adaptive_correction": cumulative_corrections,
            "mean_adaptive_correction_rate": round(cumulative_corrections / max(1, cycles), 6),
            "latest_closed_embodied_feedback_index": round(closed_feedback_index, 6),
            "latest_timestamp_utc": result["timestamp_utc"],
        }

        if persist:
            _append_jsonl(self.history_path, result)
            _write_json(self.latest_path, result)
            _write_json(self.index_path, index)
            result["persisted"] = True

        return result

__all__ = [
    "ClosedEmbodiedFeedbackValidationLoop",
    "PRIMITIVE",
    "REFINEMENT",
    "DEPENDENCIES",
]
