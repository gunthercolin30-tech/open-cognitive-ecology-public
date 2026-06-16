"""
Q8 — persistent_physical_feedback_loop

Persistent governed physical feedback loop for Open Cognitive Ecology.

Functional validation only:
this module measures observable, auditable loop properties and does not claim
phenomenal subjectivity.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, lower: float = 0.0, upper: float = 1.0) -> float:
    try:
        numeric = float(value)
    except Exception:
        numeric = lower
    if math.isnan(numeric) or math.isinf(numeric):
        numeric = lower
    return max(lower, min(upper, numeric))


def _safe_read_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        return {}
    return {}


def _history_count(path: Path) -> int:
    try:
        if not path.exists():
            return 0
        return len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])
    except Exception:
        return 0


def _safe_mean(values: List[float], default: float = 0.0) -> float:
    values = [float(v) for v in values if isinstance(v, (int, float))]
    return mean(values) if values else default


class PersistentPhysicalFeedbackLoop:
    """
    Closes the persistent physical loop:

    observe -> detect gap -> select intervention -> run governed experiment
    -> track environmental impact -> adapt strategy -> persist next cycle.

    Q8 is not a low-level perception/action loop. It orchestrates persistent
    multi-cycle adaptation over Q1-Q7 and the embodied G feedback modules.
    """

    primitive = "persistent_physical_feedback_loop"
    refinement = "Q8-R1"
    schema_version = "Q8.persistent_physical_feedback_loop.v1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.output_dir = self.root / "physical_feedback"
        self.state_path = self.output_dir / "persistent_physical_feedback_loop.json"
        self.latest_path = self.output_dir / "latest_persistent_physical_feedback_loop.json"
        self.history_path = self.output_dir / "persistent_physical_feedback_loop_history.jsonl"

    def _load_context(self) -> Dict[str, Dict[str, Any]]:
        return {
            "q1": _safe_read_json(self.root / "physical_ecology" / "latest_physical_infrastructure_registry.json"),
            "q2": _safe_read_json(self.root / "physical_ecology" / "latest_hardware_health_monitor.json"),
            "q3": _safe_read_json(self.root / "physical_sensors" / "latest_distributed_sensor_expansion_manager.json"),
            "q4": _safe_read_json(self.root / "physical_actuators" / "latest_real_actuator_control_layer.json"),
            "q5": _safe_read_json(self.root / "physical_safety" / "latest_physical_safety_supervisor.json"),
            "q6": _safe_read_json(self.root / "physical_experiments" / "latest_autonomous_physical_experiment_runner.json"),
            "q7": _safe_read_json(self.root / "physical_interventions" / "latest_environmental_intervention_tracker.json"),
            "g8": _safe_read_json(self.root / "sensorimotor_loops" / "latest_perception_action_feedback_loop.json"),
            "g16": _safe_read_json(
                self.root / "closed_embodied_feedback_validation_loop" / "latest_closed_embodied_feedback_validation_loop.json"
            ),
            "g18": _safe_read_json(
                self.root / "runtime_experiments" / "environmental_grounding_longitudinal_observatory" / "environmental_grounding_longitudinal_state.json"
            ),
        }

    def _normalize_inputs(self, inputs: Any) -> Dict[str, Any]:
        if isinstance(inputs, dict):
            return dict(inputs)
        return {}

    def _detect_gap(self, context: Dict[str, Dict[str, Any]], inputs: Dict[str, Any]) -> Dict[str, Any]:
        q2_health = _clamp(context["q2"].get("hardware_health_index", 0.75))
        q3_coverage = _clamp(context["q3"].get("sensor_network_coverage", 0.5))
        q5_safety = _clamp(context["q5"].get("physical_safety_score", 0.75))
        q6_success = _clamp(context["q6"].get("physical_experiment_success_rate", 0.75))
        q7_effectiveness = _clamp(context["q7"].get("intervention_effectiveness", 0.5))
        q7_confidence = _clamp(context["q7"].get("causal_confidence_score", 0.5))

        target = _clamp(inputs.get("target_stability", 0.85))
        observed_stability = _clamp(
            0.18 * q2_health
            + 0.16 * q3_coverage
            + 0.20 * q5_safety
            + 0.14 * q6_success
            + 0.17 * q7_effectiveness
            + 0.15 * q7_confidence
        )
        gap = _clamp(target - observed_stability)

        if gap >= 0.35:
            severity = "critical"
        elif gap >= 0.20:
            severity = "high"
        elif gap >= 0.08:
            severity = "moderate"
        else:
            severity = "low"

        return {
            "target_stability": round(target, 6),
            "observed_stability": round(observed_stability, 6),
            "feedback_gap": round(gap, 6),
            "gap_severity": severity,
            "component_scores": {
                "hardware_health_index": q2_health,
                "sensor_network_coverage": q3_coverage,
                "physical_safety_score": q5_safety,
                "physical_experiment_success_rate": q6_success,
                "intervention_effectiveness": q7_effectiveness,
                "causal_confidence_score": q7_confidence,
            },
        }

    def _select_adaptation(self, gap: Dict[str, Any], context: Dict[str, Dict[str, Any]], inputs: Dict[str, Any]) -> Dict[str, Any]:
        scores = gap["component_scores"]
        ranked = sorted(scores.items(), key=lambda item: item[1])
        weakest_name, weakest_score = ranked[0] if ranked else ("unknown", 0.0)

        emergency_stop = bool(inputs.get("emergency_stop", False))
        safety = _clamp(context["q5"].get("physical_safety_score", 0.75))
        real_io_allowed = bool(inputs.get("allow_real_io", False)) and safety >= 0.95 and not emergency_stop

        if weakest_name == "sensor_network_coverage":
            action = "expand_sensor_observation"
        elif weakest_name == "hardware_health_index":
            action = "reduce_physical_load"
        elif weakest_name == "physical_safety_score":
            action = "tighten_safety_envelope"
        elif weakest_name == "physical_experiment_success_rate":
            action = "repeat_dry_run_protocol"
        elif weakest_name == "intervention_effectiveness":
            action = "refine_intervention_protocol"
        else:
            action = "increase_measurement_repetition"

        if gap.get("gap_severity") == "low":
            action = "maintain_and_monitor"

        return {
            "selected_adaptation": action,
            "weakest_component": weakest_name,
            "weakest_component_score": round(float(weakest_score), 6),
            "real_io_allowed": bool(real_io_allowed),
            "dry_run_required": not bool(real_io_allowed),
            "emergency_stop_respected": not emergency_stop,
            "adaptation_authorized": not emergency_stop,
        }

    def _simulate_cycle_result(self, gap: Dict[str, Any], adaptation: Dict[str, Any], context: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        q7_effectiveness = _clamp(context["q7"].get("intervention_effectiveness", 0.5))
        q7_confidence = _clamp(context["q7"].get("causal_confidence_score", 0.5))
        q5_safety = _clamp(context["q5"].get("physical_safety_score", 0.75))
        gap_value = _clamp(gap.get("feedback_gap", 0.0))

        if not adaptation.get("adaptation_authorized", False):
            adaptation_rate = 0.0
        elif adaptation.get("selected_adaptation") == "maintain_and_monitor":
            adaptation_rate = _clamp(0.05 + 0.10 * q7_confidence)
        else:
            adaptation_rate = _clamp(0.20 * gap_value + 0.35 * q7_effectiveness + 0.25 * q7_confidence + 0.20 * q5_safety)

        adaptive_success = _clamp(0.35 * q7_effectiveness + 0.30 * q7_confidence + 0.20 * q5_safety + 0.15 * (1.0 - gap_value))
        response_latency = _clamp(1.0 - (0.55 * adaptive_success + 0.25 * q7_confidence + 0.20 * q5_safety))
        feedback_stability = _clamp(0.40 * (1.0 - gap_value) + 0.25 * q5_safety + 0.20 * q7_confidence + 0.15 * adaptive_success)

        return {
            "physical_adaptation_rate": round(adaptation_rate, 6),
            "adaptive_intervention_success_rate": round(adaptive_success, 6),
            "environmental_response_latency": round(response_latency, 6),
            "feedback_stability_index": round(feedback_stability, 6),
        }

    def step(self, inputs: Any = None, persist: bool = True) -> Dict[str, Any]:
        normalized_inputs = self._normalize_inputs(inputs)
        context = self._load_context()

        gap = self._detect_gap(context, normalized_inputs)
        adaptation = self._select_adaptation(gap, context, normalized_inputs)
        cycle = self._simulate_cycle_result(gap, adaptation, context)

        previous_cycles = _history_count(self.history_path)
        physical_feedback_cycles = previous_cycles + (1 if persist else 0)

        q_integrations = {
            "q1_registry_integrated": bool(context["q1"]),
            "q2_health_integrated": bool(context["q2"]),
            "q3_sensor_expansion_integrated": bool(context["q3"]),
            "q4_control_integrated": bool(context["q4"]),
            "q5_safety_integrated": bool(context["q5"]),
            "q6_experiment_integrated": bool(context["q6"]),
            "q7_intervention_integrated": bool(context["q7"]),
            "g8_feedback_integrated": bool(context["g8"]),
            "g16_closed_loop_integrated": bool(context["g16"]),
            "g18_longitudinal_grounding_integrated": bool(context["g18"]),
        }

        integration_score = _clamp(sum(1 for value in q_integrations.values() if value) / len(q_integrations))
        persistent_loop_viability = _clamp(
            0.22 * integration_score
            + 0.20 * cycle["feedback_stability_index"]
            + 0.20 * cycle["adaptive_intervention_success_rate"]
            + 0.16 * cycle["physical_adaptation_rate"]
            + 0.12 * (1.0 - cycle["environmental_response_latency"])
            + 0.10 * (1.0 - gap["feedback_gap"])
        )

        recommendations = []
        if not adaptation["adaptation_authorized"]:
            recommendations.append("Emergency stop active: no adaptive physical feedback cycle authorized.")
        if gap["gap_severity"] in {"high", "critical"}:
            recommendations.append("Large feedback gap detected: repeat dry-run intervention before any real I/O.")
        if cycle["feedback_stability_index"] < 0.65:
            recommendations.append("Feedback stability is below robust threshold: increase measurement repetition.")
        if not recommendations:
            recommendations.append("Persistent physical feedback loop is ready for continued governed iteration.")

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            **q_integrations,
            "physical_feedback_cycles": physical_feedback_cycles,
            "target_stability": gap["target_stability"],
            "observed_stability": gap["observed_stability"],
            "feedback_gap": gap["feedback_gap"],
            "gap_severity": gap["gap_severity"],
            "selected_adaptation": adaptation["selected_adaptation"],
            "weakest_component": adaptation["weakest_component"],
            "weakest_component_score": adaptation["weakest_component_score"],
            "adaptation_authorized": adaptation["adaptation_authorized"],
            "dry_run_required": adaptation["dry_run_required"],
            "real_io_allowed": adaptation["real_io_allowed"],
            "physical_adaptation_rate": cycle["physical_adaptation_rate"],
            "adaptive_intervention_success_rate": cycle["adaptive_intervention_success_rate"],
            "environmental_response_latency": cycle["environmental_response_latency"],
            "feedback_stability_index": cycle["feedback_stability_index"],
            "persistent_loop_viability": round(persistent_loop_viability, 6),
            "integration_score": round(integration_score, 6),
            "alert_required": (not adaptation["adaptation_authorized"]) or gap["gap_severity"] in {"high", "critical"},
            "component_scores": gap["component_scores"],
            "recommendations": recommendations,
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "physical_safety_supervisor_required": True,
                "default_dry_run": True,
                "real_io_default_blocked_without_explicit_governance": True,
                "persistent_adaptation_is_governed": True,
            },
            "timestamp_utc": _utc_now(),
            "state_path": str(self.state_path),
            "latest_path": str(self.latest_path),
            "history_path": str(self.history_path),
            "history_written": False,
        }

        if persist:
            self._persist(result)

        return result

    def _persist(self, result: Dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_path.write_text(payload + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        result["history_written"] = True
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.state_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_path.write_text(payload + "\n", encoding="utf-8")


__all__ = ["PersistentPhysicalFeedbackLoop"]
