"""
Trajectory Simulation — C6-R.2 mutation sandbox validation instrumentation.

This module makes mutation-trajectory simulation explicit, quantified and
historized. It is intended to support EvolutionSandbox without duplicating its
decision role.

It simulates candidate trajectories and exposes:
    - trajectory_count;
    - mean_projected_delta;
    - trajectory_success_rate;
    - trajectory_failure_rate;
    - trajectory_reversibility_rate;
    - trajectory_non_closure_rate;
    - trajectory_simulation_certified.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


PRIMITIVE = "trajectory_simulation"

DEPENDENCIES = [
    "trajectory_validation",
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


class TrajectorySimulation:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "trajectory_simulation_state.json"
        self.trajectories: list[dict[str, Any]] = []

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "trajectories": [],
            "metrics_history": [],
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def simulate(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})

        trajectory_id = str(
            inputs.get("trajectory_id")
            or inputs.get("mutation_id")
            or inputs.get("candidate")
            or "anonymous_trajectory"
        )

        baseline_score = _bounded(inputs.get("baseline_score", 0.90), 0.90)
        projected_score = _bounded(inputs.get("projected_score", baseline_score), baseline_score)
        projected_delta = round(projected_score - baseline_score, 4)

        reversibility_score = _bounded(inputs.get("reversibility_score", 1.0), 1.0)
        validation_score = _bounded(inputs.get("validation_score", 0.95), 0.95)
        non_closure_score = _bounded(inputs.get("non_closure_score", 0.93), 0.93)
        outcome_confidence = _bounded(inputs.get("outcome_confidence", 0.95), 0.95)
        regression_risk = _bounded(inputs.get("regression_risk", 0.0), 0.0)
        closure_pressure_delta = float(inputs.get("closure_pressure_delta", 0.0))

        degradation_detected = (
            projected_delta < 0.0
            or regression_risk > float(inputs.get("max_regression_risk", 0.10))
            or closure_pressure_delta > 0.0
            or bool(inputs.get("degradation_detected", False))
        )

        reversible = reversibility_score >= float(inputs.get("reversibility_threshold", 0.85))
        validated = validation_score >= float(inputs.get("validation_threshold", 0.85))
        non_closure_preserved = (
            non_closure_score >= float(inputs.get("non_closure_threshold", 0.85))
            and closure_pressure_delta <= 0.0
        )

        trajectory_score = _safe_mean([
            projected_score,
            reversibility_score,
            validation_score,
            non_closure_score,
            outcome_confidence,
            1.0 - regression_risk,
            1.0 if projected_delta >= 0.0 else 0.0,
        ])

        trajectory_success = (
            trajectory_score >= float(inputs.get("trajectory_success_threshold", 0.85))
            and reversible
            and validated
            and non_closure_preserved
            and not degradation_detected
        )

        trajectory_failure = not trajectory_success

        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "trajectory_id": trajectory_id,
            "baseline_score": round(baseline_score, 4),
            "projected_score": round(projected_score, 4),
            "projected_delta": projected_delta,
            "reversibility_score": round(reversibility_score, 4),
            "validation_score": round(validation_score, 4),
            "non_closure_score": round(non_closure_score, 4),
            "outcome_confidence": round(outcome_confidence, 4),
            "regression_risk": round(regression_risk, 4),
            "closure_pressure_delta": round(closure_pressure_delta, 4),
            "degradation_detected": degradation_detected,
            "reversible": reversible,
            "validated": validated,
            "non_closure_preserved": non_closure_preserved,
            "trajectory_score": round(trajectory_score, 4),
            "trajectory_success": trajectory_success,
            "trajectory_failure": trajectory_failure,
        }

    def _metrics(self, trajectories: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(trajectories)
        successful = [t for t in trajectories if t.get("trajectory_success")]
        failed = [t for t in trajectories if t.get("trajectory_failure")]
        reversible = [t for t in trajectories if t.get("reversible")]
        validated = [t for t in trajectories if t.get("validated")]
        non_closure = [t for t in trajectories if t.get("non_closure_preserved")]
        degraded = [t for t in trajectories if t.get("degradation_detected")]

        trajectory_success_rate = len(successful) / total if total else 0.0
        trajectory_failure_rate = len(failed) / total if total else 0.0
        trajectory_reversibility_rate = len(reversible) / total if total else 0.0
        trajectory_validation_rate = len(validated) / total if total else 0.0
        trajectory_non_closure_rate = len(non_closure) / total if total else 0.0
        trajectory_degradation_rate = len(degraded) / total if total else 0.0

        mean_projected_delta = _safe_mean([float(t.get("projected_delta", 0.0)) for t in trajectories], 0.0)
        mean_trajectory_score = _safe_mean([float(t.get("trajectory_score", 0.0)) for t in trajectories], 0.0)

        trajectory_simulation_certified = (
            total > 0
            and trajectory_success_rate >= 0.50
            and trajectory_reversibility_rate >= 0.90
            and trajectory_validation_rate >= 0.90
            and trajectory_non_closure_rate >= 0.90
            and trajectory_degradation_rate <= 0.10
            and mean_trajectory_score >= 0.85
        )

        return {
            "trajectory_count": total,
            "trajectory_success_rate": round(trajectory_success_rate, 4),
            "trajectory_failure_rate": round(trajectory_failure_rate, 4),
            "trajectory_reversibility_rate": round(trajectory_reversibility_rate, 4),
            "trajectory_validation_rate": round(trajectory_validation_rate, 4),
            "trajectory_non_closure_rate": round(trajectory_non_closure_rate, 4),
            "trajectory_degradation_rate": round(trajectory_degradation_rate, 4),
            "mean_projected_delta": round(mean_projected_delta, 4),
            "mean_trajectory_score": round(mean_trajectory_score, 4),
            "trajectory_simulation_certified": trajectory_simulation_certified,
        }

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        record = self.simulate(inputs)
        self.trajectories.append(record)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state.setdefault("trajectories", [])
        state["trajectories"].append(record)
        state["trajectories"] = state["trajectories"][-500:]

        trajectories = [
            item for item in state["trajectories"]
            if isinstance(item, dict)
        ]
        metrics = self._metrics(trajectories)

        state.setdefault("metrics_history", [])
        state["metrics_history"].append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **metrics,
        })
        state["metrics_history"] = state["metrics_history"][-1000:]
        self._save_state(state)

        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_SIMULATION_INSTRUMENTATION",
            **record,
            **metrics,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "simulation_explicit": True,
                "quantified": True,
                "historized": True,
                "non_closure_guard": record["non_closure_preserved"],
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        state = self._load_state()
        trajectories = [
            item for item in state.get("trajectories", [])
            if isinstance(item, dict)
        ]
        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_SIMULATION_INSTRUMENTATION",
            **self._metrics(trajectories),
            "state_path": str(self.state_path),
        }


ENGINE = TrajectorySimulation
