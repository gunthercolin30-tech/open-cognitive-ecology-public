"""
Q7 — environmental_intervention_tracker

Tracks governed physical interventions and estimates observable environmental
impact using before/after measurements. Functional validation only.
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


def _numeric_values(payload: Any, prefix: str = "") -> Dict[str, float]:
    values: Dict[str, float] = {}
    if not isinstance(payload, dict):
        return values
    for key, value in payload.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, bool):
            values[name] = 1.0 if value else 0.0
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                number = float(value)
                if not math.isnan(number) and not math.isinf(number):
                    values[name] = number
            except Exception:
                pass
        elif isinstance(value, dict):
            values.update(_numeric_values(value, name))
    return values


class EnvironmentalInterventionTracker:
    """
    Measures whether a governed physical experiment appears to produce an
    observable environmental change.

    Q7 is not an actuator executor and does not authorize physical action.
    It compares pre/post environmental states and computes:
    - environmental_impact_score
    - intervention_effectiveness
    - causal_confidence_score
    - tracked_intervention_count
    """

    primitive = "environmental_intervention_tracker"
    refinement = "Q7-R1"
    schema_version = "Q7.environmental_intervention_tracker.v1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.output_dir = self.root / "physical_interventions"
        self.state_path = self.output_dir / "environmental_intervention_tracker.json"
        self.latest_path = self.output_dir / "latest_environmental_intervention_tracker.json"
        self.history_path = self.output_dir / "environmental_intervention_tracker_history.jsonl"

    def _default_intervention(self, q6: Dict[str, Any]) -> Dict[str, Any]:
        protocol_id = q6.get("protocol_id", "Q7-default-derived-protocol")
        experiment_success = _clamp(q6.get("physical_experiment_success_rate", 0.0))
        reproducibility = _clamp(q6.get("physical_experiment_reproducibility_score", 0.0))
        measurement = _clamp(q6.get("measurement_collection_rate", 1.0))
        authorized = bool(q6.get("experiment_authorized", False))

        return {
            "intervention_id": f"Q7-derived-from-{protocol_id}",
            "source_protocol_id": protocol_id,
            "authorized": authorized,
            "expected_direction": "stabilizing",
            "pre_state": {
                "environmental_stability": round(0.50 + 0.20 * reproducibility, 6),
                "measurement_quality": round(0.50 + 0.25 * measurement, 6),
                "risk_pressure": round(0.30 + 0.20 * (1.0 - experiment_success), 6),
            },
            "post_state": {
                "environmental_stability": round(0.55 + 0.25 * reproducibility, 6),
                "measurement_quality": round(0.55 + 0.30 * measurement, 6),
                "risk_pressure": round(0.22 + 0.12 * (1.0 - experiment_success), 6),
            },
            "control_state": {
                "environmental_stability": 0.55,
                "measurement_quality": 0.60,
                "risk_pressure": 0.28,
            },
        }

    def _normalize_intervention(self, inputs: Any, q6: Dict[str, Any]) -> Dict[str, Any]:
        if inputs is None:
            return self._default_intervention(q6)
        if isinstance(inputs, dict):
            if "intervention" in inputs and isinstance(inputs["intervention"], dict):
                candidate = dict(inputs["intervention"])
            else:
                candidate = dict(inputs)
            default = self._default_intervention(q6)
            default.update(candidate)
            for key in ("pre_state", "post_state", "control_state"):
                if not isinstance(default.get(key), dict):
                    default[key] = {}
            return default
        return self._default_intervention(q6)

    def _compute_delta(self, pre_state: Dict[str, Any], post_state: Dict[str, Any]) -> Dict[str, Any]:
        pre = _numeric_values(pre_state)
        post = _numeric_values(post_state)
        common = sorted(set(pre) & set(post))
        deltas: Dict[str, float] = {}
        abs_deltas: List[float] = []
        signed_deltas: List[float] = []

        for key in common:
            delta = post[key] - pre[key]
            deltas[key] = round(delta, 6)
            abs_deltas.append(min(1.0, abs(delta)))
            signed_deltas.append(max(-1.0, min(1.0, delta)))

        mean_abs_delta = mean(abs_deltas) if abs_deltas else 0.0
        mean_signed_delta = mean(signed_deltas) if signed_deltas else 0.0

        return {
            "observed_key_count": len(common),
            "deltas": deltas,
            "mean_abs_delta": round(_clamp(mean_abs_delta), 6),
            "mean_signed_delta": round(max(-1.0, min(1.0, mean_signed_delta)), 6),
        }

    def _causal_estimate(
        self,
        delta: Dict[str, Any],
        intervention: Dict[str, Any],
        q6: Dict[str, Any],
        q5: Dict[str, Any],
    ) -> Dict[str, Any]:
        observed_keys = int(delta.get("observed_key_count", 0))
        mean_abs_delta = _clamp(delta.get("mean_abs_delta", 0.0))
        mean_signed = float(delta.get("mean_signed_delta", 0.0))
        authorized = bool(intervention.get("authorized", False))
        expected_direction = str(intervention.get("expected_direction", "stabilizing")).lower()

        q6_success = _clamp(q6.get("physical_experiment_success_rate", 0.0))
        q6_repro = _clamp(q6.get("physical_experiment_reproducibility_score", 0.0))
        q6_measure = _clamp(q6.get("measurement_collection_rate", 0.0))
        q5_safety = _clamp(q5.get("physical_safety_score", 0.75))

        direction_alignment = 0.5
        if expected_direction in {"positive", "increase", "stabilizing", "improving"}:
            direction_alignment = _clamp(0.5 + max(-0.5, min(0.5, mean_signed)))
        elif expected_direction in {"negative", "decrease", "reducing"}:
            direction_alignment = _clamp(0.5 - max(-0.5, min(0.5, mean_signed)))

        evidence_density = _clamp(observed_keys / 5.0)
        intervention_traceability = 1.0 if authorized else 0.35

        environmental_impact_score = _clamp(
            0.55 * mean_abs_delta
            + 0.20 * direction_alignment
            + 0.15 * evidence_density
            + 0.10 * q6_measure
        )

        intervention_effectiveness = _clamp(
            0.35 * environmental_impact_score
            + 0.25 * direction_alignment
            + 0.20 * q6_success
            + 0.10 * q5_safety
            + 0.10 * intervention_traceability
        )

        causal_confidence_score = _clamp(
            0.25 * q6_repro
            + 0.25 * q6_measure
            + 0.20 * evidence_density
            + 0.15 * intervention_traceability
            + 0.15 * q5_safety
        )

        return {
            "environmental_impact_score": round(environmental_impact_score, 6),
            "intervention_effectiveness": round(intervention_effectiveness, 6),
            "causal_confidence_score": round(causal_confidence_score, 6),
            "direction_alignment_score": round(direction_alignment, 6),
            "evidence_density": round(evidence_density, 6),
            "intervention_traceability": round(intervention_traceability, 6),
        }

    def step(self, inputs: Any = None, persist: bool = True) -> Dict[str, Any]:
        q1 = _safe_read_json(self.root / "physical_ecology" / "latest_physical_infrastructure_registry.json")
        q2 = _safe_read_json(self.root / "physical_ecology" / "latest_hardware_health_monitor.json")
        q3 = _safe_read_json(self.root / "physical_sensors" / "latest_distributed_sensor_expansion_manager.json")
        q4 = _safe_read_json(self.root / "physical_actuators" / "latest_real_actuator_control_layer.json")
        q5 = _safe_read_json(self.root / "physical_safety" / "latest_physical_safety_supervisor.json")
        q6 = _safe_read_json(self.root / "physical_experiments" / "latest_autonomous_physical_experiment_runner.json")
        g18 = _safe_read_json(
            self.root / "runtime_experiments" / "environmental_grounding_longitudinal_observatory" / "environmental_grounding_longitudinal_state.json"
        )

        intervention = self._normalize_intervention(inputs, q6)
        delta = self._compute_delta(
            intervention.get("pre_state", {}),
            intervention.get("post_state", {}),
        )
        causal = self._causal_estimate(delta, intervention, q6, q5)

        tracked_intervention_count = _history_count(self.history_path) + (1 if persist else 0)
        q7_readiness = _clamp(
            0.14 * _clamp(q1.get("physical_asset_coverage", 0.5))
            + 0.14 * _clamp(q2.get("hardware_health_index", 0.7))
            + 0.14 * _clamp(q3.get("sensor_network_coverage", 0.5))
            + 0.14 * _clamp(q4.get("real_action_success_rate", 0.75))
            + 0.16 * _clamp(q5.get("physical_safety_score", 0.75))
            + 0.16 * _clamp(q6.get("physical_experiment_reproducibility_score", 0.5))
            + 0.12 * causal["causal_confidence_score"]
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            "intervention_id": intervention.get("intervention_id", "Q7-unnamed-intervention"),
            "source_protocol_id": intervention.get("source_protocol_id"),
            "q1_registry_integrated": bool(q1),
            "q2_health_integrated": bool(q2),
            "q3_sensor_expansion_integrated": bool(q3),
            "q4_control_integrated": bool(q4),
            "q5_safety_integrated": bool(q5),
            "q6_experiment_integrated": bool(q6),
            "g18_longitudinal_grounding_integrated": bool(g18),
            "tracked_intervention_count": tracked_intervention_count,
            "observed_key_count": delta["observed_key_count"],
            "state_delta": delta["deltas"],
            "mean_abs_environmental_delta": delta["mean_abs_delta"],
            "mean_signed_environmental_delta": delta["mean_signed_delta"],
            "environmental_impact_score": causal["environmental_impact_score"],
            "intervention_effectiveness": causal["intervention_effectiveness"],
            "causal_confidence_score": causal["causal_confidence_score"],
            "direction_alignment_score": causal["direction_alignment_score"],
            "evidence_density": causal["evidence_density"],
            "q7_readiness_index": round(q7_readiness, 6),
            "intervention_authorized": bool(intervention.get("authorized", False)) and bool(q6.get("experiment_authorized", False)),
            "alert_required": causal["causal_confidence_score"] < 0.4 or not bool(intervention.get("authorized", False)),
            "pre_state": intervention.get("pre_state", {}),
            "post_state": intervention.get("post_state", {}),
            "control_state": intervention.get("control_state", {}),
            "recommendations": self._recommendations(causal, intervention, q6),
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "causal_claim_is_probabilistic": True,
                "physical_safety_supervisor_required": True,
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

    def _recommendations(self, causal: Dict[str, Any], intervention: Dict[str, Any], q6: Dict[str, Any]) -> List[str]:
        recommendations: List[str] = []
        if not bool(intervention.get("authorized", False)):
            recommendations.append("Intervention was not authorized: treat impact estimate as diagnostic only.")
        if not bool(q6.get("experiment_authorized", False)):
            recommendations.append("No authorized Q6 experiment available: repeat under governed protocol.")
        if causal["causal_confidence_score"] < 0.5:
            recommendations.append("Causal confidence is weak: increase sensor coverage or repeat the intervention.")
        if causal["environmental_impact_score"] < 0.2:
            recommendations.append("Observed environmental impact is low: refine intervention intensity or measurement window.")
        if not recommendations:
            recommendations.append("Intervention tracking is suitable for Q8 persistent feedback loop integration.")
        return recommendations

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


__all__ = ["EnvironmentalInterventionTracker"]
