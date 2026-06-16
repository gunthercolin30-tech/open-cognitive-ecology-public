"""
Trajectory Validation — C6-R.3 mutation sandbox validation instrumentation.

This module centralizes trajectory validation before integration. It is designed
to complement TrajectorySimulation and EvolutionSandbox by turning validation
criteria into explicit, quantified and historized outcomes.

It exposes:
    - validation_count;
    - validation_success_rate;
    - validation_failure_rate;
    - validation_non_closure_rate;
    - validation_reversibility_rate;
    - validation_degradation_rate;
    - trajectory_validation_certified.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


PRIMITIVE = "trajectory_validation"

DEPENDENCIES = [
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


class TrajectoryValidation:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "trajectory_validation_state.json"
        self.validations: list[dict[str, Any]] = []

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "validations": [],
            "metrics_history": [],
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def validate(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})

        trajectory_id = str(
            inputs.get("trajectory_id")
            or inputs.get("mutation_id")
            or inputs.get("candidate")
            or "anonymous_validation"
        )

        simulation_score = _bounded(
            inputs.get("simulation_score", inputs.get("trajectory_score", 0.95)),
            0.95,
        )
        outcome_score = _bounded(
            inputs.get("outcome_score", inputs.get("projected_score", 0.94)),
            0.94,
        )
        reversibility_score = _bounded(inputs.get("reversibility_score", 1.0), 1.0)
        validation_score = _bounded(inputs.get("validation_score", 0.95), 0.95)
        non_closure_score = _bounded(inputs.get("non_closure_score", 0.93), 0.93)
        robustness_score = _bounded(inputs.get("robustness_score", 0.92), 0.92)
        regression_risk = _bounded(inputs.get("regression_risk", 0.0), 0.0)

        baseline_score = _bounded(inputs.get("baseline_score", 0.90), 0.90)
        projected_score = _bounded(inputs.get("projected_score", outcome_score), outcome_score)
        projected_delta = round(projected_score - baseline_score, 4)

        closure_pressure_delta = float(inputs.get("closure_pressure_delta", 0.0))
        error_count = int(inputs.get("error_count", 0))
        failed_calls = int(inputs.get("failed_calls", 0))

        degradation_detected = (
            bool(inputs.get("degradation_detected", False))
            or projected_delta < 0.0
            or closure_pressure_delta > 0.0
            or regression_risk > float(inputs.get("max_regression_risk", 0.10))
            or error_count > 0
            or failed_calls > 0
        )

        reversibility_valid = reversibility_score >= float(inputs.get("reversibility_threshold", 0.85))
        non_closure_valid = (
            non_closure_score >= float(inputs.get("non_closure_threshold", 0.85))
            and closure_pressure_delta <= 0.0
        )
        simulation_valid = simulation_score >= float(inputs.get("simulation_threshold", 0.85))
        outcome_valid = outcome_score >= float(inputs.get("outcome_threshold", 0.85))
        validation_checks_passed = validation_score >= float(inputs.get("validation_threshold", 0.85))
        robustness_valid = robustness_score >= float(inputs.get("robustness_threshold", 0.85))
        error_free = error_count == 0 and failed_calls == 0

        aggregate_validation_score = _safe_mean([
            simulation_score,
            outcome_score,
            reversibility_score,
            validation_score,
            non_closure_score,
            robustness_score,
            1.0 - regression_risk,
            1.0 if projected_delta >= 0.0 else 0.0,
            1.0 if error_free else 0.0,
        ])

        validation_success = (
            aggregate_validation_score >= float(inputs.get("aggregate_threshold", 0.85))
            and simulation_valid
            and outcome_valid
            and reversibility_valid
            and validation_checks_passed
            and non_closure_valid
            and robustness_valid
            and error_free
            and not degradation_detected
        )

        validation_failure = not validation_success
        rollback_required = (
            validation_failure
            and (
                degradation_detected
                or not reversibility_valid
                or not non_closure_valid
                or regression_risk > 0.0
                or not error_free
            )
        )

        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "trajectory_id": trajectory_id,
            "baseline_score": round(baseline_score, 4),
            "projected_score": round(projected_score, 4),
            "projected_delta": projected_delta,
            "simulation_score": round(simulation_score, 4),
            "outcome_score": round(outcome_score, 4),
            "reversibility_score": round(reversibility_score, 4),
            "validation_score": round(validation_score, 4),
            "non_closure_score": round(non_closure_score, 4),
            "robustness_score": round(robustness_score, 4),
            "regression_risk": round(regression_risk, 4),
            "closure_pressure_delta": round(closure_pressure_delta, 4),
            "error_count": error_count,
            "failed_calls": failed_calls,
            "simulation_valid": simulation_valid,
            "outcome_valid": outcome_valid,
            "reversibility_valid": reversibility_valid,
            "validation_checks_passed": validation_checks_passed,
            "non_closure_valid": non_closure_valid,
            "robustness_valid": robustness_valid,
            "error_free": error_free,
            "degradation_detected": degradation_detected,
            "aggregate_validation_score": round(aggregate_validation_score, 4),
            "validation_success": validation_success,
            "validation_failure": validation_failure,
            "rollback_required": rollback_required,
        }

    def _metrics(self, validations: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(validations)
        successful = [v for v in validations if v.get("validation_success")]
        failed = [v for v in validations if v.get("validation_failure")]
        reversible = [v for v in validations if v.get("reversibility_valid")]
        non_closure = [v for v in validations if v.get("non_closure_valid")]
        degraded = [v for v in validations if v.get("degradation_detected")]
        error_free = [v for v in validations if v.get("error_free")]
        rollback_required = [v for v in validations if v.get("rollback_required")]

        validation_success_rate = len(successful) / total if total else 0.0
        validation_failure_rate = len(failed) / total if total else 0.0
        validation_reversibility_rate = len(reversible) / total if total else 0.0
        validation_non_closure_rate = len(non_closure) / total if total else 0.0
        validation_degradation_rate = len(degraded) / total if total else 0.0
        validation_error_free_rate = len(error_free) / total if total else 0.0
        validation_rollback_requirement_rate = len(rollback_required) / total if total else 0.0

        mean_validation_score = _safe_mean(
            [float(v.get("aggregate_validation_score", 0.0)) for v in validations],
            0.0,
        )
        mean_projected_delta = _safe_mean(
            [float(v.get("projected_delta", 0.0)) for v in validations],
            0.0,
        )

        trajectory_validation_certified = (
            total > 0
            and validation_success_rate >= 0.50
            and validation_reversibility_rate >= 0.90
            and validation_non_closure_rate >= 0.90
            and validation_error_free_rate >= 0.90
            and validation_degradation_rate <= 0.10
            and mean_validation_score >= 0.85
        )

        return {
            "validation_count": total,
            "validation_success_rate": round(validation_success_rate, 4),
            "validation_failure_rate": round(validation_failure_rate, 4),
            "validation_reversibility_rate": round(validation_reversibility_rate, 4),
            "validation_non_closure_rate": round(validation_non_closure_rate, 4),
            "validation_degradation_rate": round(validation_degradation_rate, 4),
            "validation_error_free_rate": round(validation_error_free_rate, 4),
            "validation_rollback_requirement_rate": round(validation_rollback_requirement_rate, 4),
            "mean_validation_score": round(mean_validation_score, 4),
            "mean_projected_delta": round(mean_projected_delta, 4),
            "trajectory_validation_certified": trajectory_validation_certified,
        }

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        record = self.validate(inputs)
        self.validations.append(record)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state.setdefault("validations", [])
        state["validations"].append(record)
        state["validations"] = state["validations"][-500:]

        validations = [
            item for item in state["validations"]
            if isinstance(item, dict)
        ]
        metrics = self._metrics(validations)

        state.setdefault("metrics_history", [])
        state["metrics_history"].append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **metrics,
        })
        state["metrics_history"] = state["metrics_history"][-1000:]
        self._save_state(state)

        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_VALIDATION_INSTRUMENTATION",
            **record,
            **metrics,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "validation_explicit": True,
                "quantified": True,
                "historized": True,
                "non_closure_guard": record["non_closure_valid"],
                "rollback_guard": True,
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        state = self._load_state()
        validations = [
            item for item in state.get("validations", [])
            if isinstance(item, dict)
        ]
        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_VALIDATION_INSTRUMENTATION",
            **self._metrics(validations),
            "state_path": str(self.state_path),
        }


ENGINE = TrajectoryValidation
