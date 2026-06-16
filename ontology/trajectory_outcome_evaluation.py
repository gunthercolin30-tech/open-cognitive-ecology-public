"""
Trajectory Outcome Evaluation — C6-R.5 mutation sandbox outcome instrumentation.

This module centralizes outcome evaluation for simulated, validated and
reversible mutation trajectories. It does not execute mutations. It evaluates
whether a proposed trajectory outcome is beneficial, harmful, stable,
non-closure preserving and sufficiently confident before any integration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


PRIMITIVE = "trajectory_outcome_evaluation"

DEPENDENCIES = [
    "trajectory_simulation",
    "trajectory_validation",
    "trajectory_reversibility",
    "trajectory_evaluation",
    "trajectory_reward_assignment",
    "trajectory_feedback",
    "trajectory_failure",
    "trajectory_recovery",
    "trajectory_robustness",
    "trajectory_stability",
    "mutational_robustness",
    "evolvability",
    "adaptive_capacity",
    "evaluation",
    "monitoring",
    "non_closure_certification_protocol",
    "openness_preservation_supervisor",
    "anti_closure_metaconstraint",
]


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _safe_mean(values: list[float], default: float = 0.0) -> float:
    filtered = [float(v) for v in values if v is not None]
    if not filtered:
        return default
    return round(sum(filtered) / len(filtered), 4)


class TrajectoryOutcomeEvaluation:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "trajectory_outcome_evaluation_state.json"
        self.evaluations: list[dict[str, Any]] = []

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"primitive": PRIMITIVE, "evaluations": [], "metrics_history": []}

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    def evaluate(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})

        trajectory_id = str(
            inputs.get("trajectory_id")
            or inputs.get("mutation_id")
            or inputs.get("candidate")
            or "anonymous_outcome_evaluation"
        )

        baseline_score = _bounded(inputs.get("baseline_score", 0.90), 0.90)
        projected_score = _bounded(inputs.get("projected_score", inputs.get("outcome_score", baseline_score)), baseline_score)
        expected_delta = round(projected_score - baseline_score, 4)

        observed_score = _bounded(inputs.get("observed_score", projected_score), projected_score)
        observed_delta = round(observed_score - baseline_score, 4)

        simulation_score = _bounded(inputs.get("simulation_score", inputs.get("trajectory_score", 0.95)), 0.95)
        validation_score = _bounded(inputs.get("validation_score", 0.95), 0.95)
        reversibility_score = _bounded(inputs.get("reversibility_score", 1.0), 1.0)
        outcome_confidence = _bounded(inputs.get("outcome_confidence", 0.95), 0.95)
        stability_score = _bounded(inputs.get("stability_score", inputs.get("trajectory_stability_score", 0.92)), 0.92)
        robustness_score = _bounded(inputs.get("robustness_score", 0.92), 0.92)
        adaptive_capacity_score = _bounded(inputs.get("adaptive_capacity_score", 0.90), 0.90)
        evolvability_score = _bounded(inputs.get("evolvability_score", 0.90), 0.90)
        non_closure_score = _bounded(inputs.get("non_closure_score", 0.93), 0.93)
        regression_risk = _bounded(inputs.get("regression_risk", 0.0), 0.0)

        closure_pressure_delta = float(inputs.get("closure_pressure_delta", 0.0))
        error_count = int(inputs.get("error_count", 0))
        failed_calls = int(inputs.get("failed_calls", 0))

        expected_gain = expected_delta > 0.0
        expected_loss = expected_delta < 0.0
        observed_gain = observed_delta > 0.0
        observed_loss = observed_delta < 0.0

        degradation_detected = (
            bool(inputs.get("degradation_detected", False))
            or expected_loss
            or observed_loss
            or regression_risk > float(inputs.get("max_regression_risk", 0.10))
            or closure_pressure_delta > 0.0
            or error_count > 0
            or failed_calls > 0
        )

        confidence_valid = outcome_confidence >= float(inputs.get("confidence_threshold", 0.85))
        stability_valid = stability_score >= float(inputs.get("stability_threshold", 0.85))
        robustness_valid = robustness_score >= float(inputs.get("robustness_threshold", 0.85))
        validation_valid = validation_score >= float(inputs.get("validation_threshold", 0.85))
        simulation_valid = simulation_score >= float(inputs.get("simulation_threshold", 0.85))
        reversibility_valid = reversibility_score >= float(inputs.get("reversibility_threshold", 0.85))
        adaptive_capacity_valid = adaptive_capacity_score >= float(inputs.get("adaptive_capacity_threshold", 0.80))
        evolvability_valid = evolvability_score >= float(inputs.get("evolvability_threshold", 0.80))
        non_closure_preserved = (
            non_closure_score >= float(inputs.get("non_closure_threshold", 0.85))
            and closure_pressure_delta <= 0.0
        )
        error_free = error_count == 0 and failed_calls == 0

        outcome_score = _safe_mean([
            projected_score,
            observed_score,
            simulation_score,
            validation_score,
            reversibility_score,
            outcome_confidence,
            stability_score,
            robustness_score,
            adaptive_capacity_score,
            evolvability_score,
            non_closure_score,
            1.0 - regression_risk,
            1.0 if expected_gain else 0.0,
            1.0 if observed_gain else 0.0,
            1.0 if error_free else 0.0,
        ])

        beneficial_outcome = (
            expected_gain
            and observed_gain
            and simulation_valid
            and validation_valid
            and reversibility_valid
            and confidence_valid
            and stability_valid
            and robustness_valid
            and adaptive_capacity_valid
            and evolvability_valid
            and non_closure_preserved
            and error_free
            and not degradation_detected
        )

        harmful_outcome = (
            degradation_detected
            or expected_loss
            or observed_loss
            or not non_closure_preserved
            or not validation_valid
            or not simulation_valid
            or not robustness_valid
            or not error_free
        )

        outcome_success = beneficial_outcome and outcome_score >= float(inputs.get("outcome_success_threshold", 0.85))
        outcome_failure = not outcome_success

        rollback_required = (
            outcome_failure
            and (
                harmful_outcome
                or degradation_detected
                or not non_closure_preserved
                or not reversibility_valid
                or not error_free
            )
        )

        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "trajectory_id": trajectory_id,
            "baseline_score": round(baseline_score, 4),
            "projected_score": round(projected_score, 4),
            "observed_score": round(observed_score, 4),
            "expected_delta": expected_delta,
            "observed_delta": observed_delta,
            "simulation_score": round(simulation_score, 4),
            "validation_score": round(validation_score, 4),
            "reversibility_score": round(reversibility_score, 4),
            "outcome_confidence": round(outcome_confidence, 4),
            "stability_score": round(stability_score, 4),
            "robustness_score": round(robustness_score, 4),
            "adaptive_capacity_score": round(adaptive_capacity_score, 4),
            "evolvability_score": round(evolvability_score, 4),
            "non_closure_score": round(non_closure_score, 4),
            "regression_risk": round(regression_risk, 4),
            "closure_pressure_delta": round(closure_pressure_delta, 4),
            "error_count": error_count,
            "failed_calls": failed_calls,
            "expected_gain": expected_gain,
            "expected_loss": expected_loss,
            "observed_gain": observed_gain,
            "observed_loss": observed_loss,
            "simulation_valid": simulation_valid,
            "validation_valid": validation_valid,
            "reversibility_valid": reversibility_valid,
            "confidence_valid": confidence_valid,
            "stability_valid": stability_valid,
            "robustness_valid": robustness_valid,
            "adaptive_capacity_valid": adaptive_capacity_valid,
            "evolvability_valid": evolvability_valid,
            "non_closure_preserved": non_closure_preserved,
            "error_free": error_free,
            "degradation_detected": degradation_detected,
            "outcome_score": round(outcome_score, 4),
            "beneficial_outcome": beneficial_outcome,
            "harmful_outcome": harmful_outcome,
            "outcome_success": outcome_success,
            "outcome_failure": outcome_failure,
            "rollback_required": rollback_required,
        }

    def _metrics(self, evaluations: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(evaluations)
        successful = [e for e in evaluations if e.get("outcome_success")]
        failed = [e for e in evaluations if e.get("outcome_failure")]
        beneficial = [e for e in evaluations if e.get("beneficial_outcome")]
        harmful = [e for e in evaluations if e.get("harmful_outcome")]
        expected_gain = [e for e in evaluations if e.get("expected_gain")]
        expected_loss = [e for e in evaluations if e.get("expected_loss")]
        confident = [e for e in evaluations if e.get("confidence_valid")]
        stable = [e for e in evaluations if e.get("stability_valid")]
        non_closure = [e for e in evaluations if e.get("non_closure_preserved")]
        reversible = [e for e in evaluations if e.get("reversibility_valid")]
        degraded = [e for e in evaluations if e.get("degradation_detected")]
        rollback_required = [e for e in evaluations if e.get("rollback_required")]

        outcome_success_rate = len(successful) / total if total else 0.0
        outcome_failure_rate = len(failed) / total if total else 0.0
        beneficial_outcome_rate = len(beneficial) / total if total else 0.0
        harmful_outcome_rate = len(harmful) / total if total else 0.0
        expected_gain_rate = len(expected_gain) / total if total else 0.0
        expected_loss_rate = len(expected_loss) / total if total else 0.0
        outcome_confidence_rate = len(confident) / total if total else 0.0
        outcome_stability_rate = len(stable) / total if total else 0.0
        outcome_non_closure_rate = len(non_closure) / total if total else 0.0
        outcome_reversibility_rate = len(reversible) / total if total else 0.0
        outcome_degradation_rate = len(degraded) / total if total else 0.0
        outcome_rollback_requirement_rate = len(rollback_required) / total if total else 0.0

        mean_outcome_score = _safe_mean([float(e.get("outcome_score", 0.0)) for e in evaluations], 0.0)
        mean_expected_delta = _safe_mean([float(e.get("expected_delta", 0.0)) for e in evaluations], 0.0)
        mean_observed_delta = _safe_mean([float(e.get("observed_delta", 0.0)) for e in evaluations], 0.0)

        trajectory_outcome_evaluation_certified = (
            total > 0
            and outcome_success_rate >= 0.50
            and beneficial_outcome_rate >= 0.50
            and harmful_outcome_rate <= 0.10
            and expected_gain_rate >= 0.70
            and expected_loss_rate <= 0.10
            and outcome_confidence_rate >= 0.90
            and outcome_stability_rate >= 0.90
            and outcome_non_closure_rate >= 0.90
            and outcome_reversibility_rate >= 0.90
            and outcome_degradation_rate <= 0.10
            and mean_outcome_score >= 0.85
        )

        return {
            "outcome_count": total,
            "outcome_success_rate": round(outcome_success_rate, 4),
            "outcome_failure_rate": round(outcome_failure_rate, 4),
            "beneficial_outcome_rate": round(beneficial_outcome_rate, 4),
            "harmful_outcome_rate": round(harmful_outcome_rate, 4),
            "expected_gain_rate": round(expected_gain_rate, 4),
            "expected_loss_rate": round(expected_loss_rate, 4),
            "outcome_confidence_rate": round(outcome_confidence_rate, 4),
            "outcome_stability_rate": round(outcome_stability_rate, 4),
            "outcome_non_closure_rate": round(outcome_non_closure_rate, 4),
            "outcome_reversibility_rate": round(outcome_reversibility_rate, 4),
            "outcome_degradation_rate": round(outcome_degradation_rate, 4),
            "outcome_rollback_requirement_rate": round(outcome_rollback_requirement_rate, 4),
            "mean_outcome_score": round(mean_outcome_score, 4),
            "mean_expected_delta": round(mean_expected_delta, 4),
            "mean_observed_delta": round(mean_observed_delta, 4),
            "trajectory_outcome_evaluation_certified": trajectory_outcome_evaluation_certified,
        }

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        record = self.evaluate(inputs)
        self.evaluations.append(record)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state.setdefault("evaluations", [])
        state["evaluations"].append(record)
        state["evaluations"] = state["evaluations"][-500:]

        evaluations = [item for item in state["evaluations"] if isinstance(item, dict)]
        metrics = self._metrics(evaluations)

        state.setdefault("metrics_history", [])
        state["metrics_history"].append({"timestamp_utc": datetime.now(timezone.utc).isoformat(), **metrics})
        state["metrics_history"] = state["metrics_history"][-1000:]
        self._save_state(state)

        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_OUTCOME_EVALUATION_INSTRUMENTATION",
            **record,
            **metrics,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "outcome_evaluation_explicit": True,
                "quantified": True,
                "historized": True,
                "non_closure_guard": record["non_closure_preserved"],
                "rollback_guard": True,
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        state = self._load_state()
        evaluations = [item for item in state.get("evaluations", []) if isinstance(item, dict)]
        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_OUTCOME_EVALUATION_INSTRUMENTATION",
            **self._metrics(evaluations),
            "state_path": str(self.state_path),
        }


ENGINE = TrajectoryOutcomeEvaluation
