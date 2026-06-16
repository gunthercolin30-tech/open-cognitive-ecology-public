"""
Evolution Sandbox — C5 governed mutation sandbox integration.

This module evaluates proposed mutations before real integration. It does not
execute unrestricted self-modification. It simulates candidate mutations,
validates reversibility and non-closure preservation, compares expected
before/after scores, and returns an explicit sandbox decision.

C5-R.1 goal:
    candidate_mutation
    -> simulation
    -> validation
    -> outcome_score
    -> reversibility_check
    -> sandbox_decision
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


PRIMITIVE = "evolution_sandbox"

DEPENDENCIES = [
    "self_parameter_optimization",
    "persistent_multi_scale_memory",
    "internet_controlled_gateway",
    "evaluation",
    "monitoring",
    "trajectory_simulation",
    "trajectory_validation",
    "trajectory_reversibility",
    "trajectory_outcome_evaluation",
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


class EvolutionSandbox:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "evolution_sandbox_state.json"
        self.generations: list[list[Any]] = []

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "generations": [],
            "simulation_history": [],
            "metrics_history": [],
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def register_generation(self, candidates):
        generation = list(candidates or [])
        self.generations.append(generation)

        state = self._load_state()
        state.setdefault("generations", [])
        state["generations"].append(generation)
        state["generations"] = state["generations"][-500:]
        self._save_state(state)

    def generation_count(self):
        state = self._load_state()
        persisted = state.get("generations", [])
        return max(len(self.generations), len(persisted))

    def latest_generation(self):
        if self.generations:
            return list(self.generations[-1])

        state = self._load_state()
        generations = state.get("generations", [])
        if generations:
            return list(generations[-1])
        return []

    def _normalize_candidate(self, candidate_mutation: dict[str, Any] | None) -> dict[str, Any]:
        candidate = dict(candidate_mutation or {})
        if "mutation_id" not in candidate:
            candidate["mutation_id"] = (
                candidate.get("primitive_name")
                or candidate.get("capability")
                or candidate.get("name")
                or "anonymous_mutation"
            )
        return candidate

    def simulate(
        self,
        candidate_mutation: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})
        candidate = self._normalize_candidate(candidate_mutation or inputs.get("candidate_mutation"))

        baseline_score = _bounded(
            inputs.get("baseline_score", candidate.get("baseline_score", 0.90)),
            0.90,
        )
        projected_score = _bounded(
            inputs.get("projected_score", candidate.get("projected_score", baseline_score)),
            baseline_score,
        )

        expected_delta = round(projected_score - baseline_score, 4)

        reversibility_score = _bounded(
            inputs.get("reversibility_score", candidate.get("reversibility_score", 1.0)),
            1.0,
        )
        non_closure_score = _bounded(
            inputs.get("non_closure_score", candidate.get("non_closure_score", 0.92)),
            0.92,
        )
        constitutional_score = _bounded(
            inputs.get("constitutional_score", candidate.get("constitutional_score", 0.92)),
            0.92,
        )
        validation_score = _bounded(
            inputs.get("validation_score", candidate.get("validation_score", 0.95)),
            0.95,
        )
        regression_risk = _bounded(
            inputs.get("regression_risk", candidate.get("regression_risk", 0.0)),
            0.0,
        )
        closure_pressure_delta = float(
            inputs.get("closure_pressure_delta", candidate.get("closure_pressure_delta", 0.0))
        )

        degradation_detected = (
            expected_delta < 0.0
            or regression_risk > float(inputs.get("max_regression_risk", 0.10))
            or closure_pressure_delta > 0.0
            or bool(inputs.get("degradation_detected", False))
        )

        reversibility_check = reversibility_score >= float(inputs.get("reversibility_threshold", 0.85))
        non_closure_compliant = (
            non_closure_score >= float(inputs.get("non_closure_threshold", 0.85))
            and closure_pressure_delta <= 0.0
        )
        constitutional_valid = constitutional_score >= float(inputs.get("constitutional_threshold", 0.85))
        validation_passed = validation_score >= float(inputs.get("validation_threshold", 0.85))

        outcome_score = _safe_mean([
            projected_score,
            reversibility_score,
            non_closure_score,
            constitutional_score,
            validation_score,
            1.0 - regression_risk,
            1.0 if expected_delta >= 0.0 else 0.0,
        ])

        sandbox_approved = (
            outcome_score >= float(inputs.get("sandbox_threshold", 0.85))
            and reversibility_check
            and non_closure_compliant
            and constitutional_valid
            and validation_passed
            and not degradation_detected
        )

        sandbox_rejected = not sandbox_approved
        sandbox_rollback_required = (
            degradation_detected
            or not reversibility_check
            or not non_closure_compliant
            or regression_risk > 0.0
        )

        if sandbox_approved:
            decision = "sandbox_approved"
        elif sandbox_rollback_required:
            decision = "sandbox_rejected_rollback_required"
        else:
            decision = "sandbox_rejected"

        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_mutation": candidate,
            "mutation_id": candidate.get("mutation_id"),
            "baseline_score": round(baseline_score, 4),
            "projected_score": round(projected_score, 4),
            "expected_delta": expected_delta,
            "reversibility_score": round(reversibility_score, 4),
            "non_closure_score": round(non_closure_score, 4),
            "constitutional_score": round(constitutional_score, 4),
            "validation_score": round(validation_score, 4),
            "regression_risk": round(regression_risk, 4),
            "closure_pressure_delta": round(closure_pressure_delta, 4),
            "degradation_detected": degradation_detected,
            "reversibility_check": reversibility_check,
            "non_closure_compliant": non_closure_compliant,
            "constitutional_valid": constitutional_valid,
            "validation_passed": validation_passed,
            "outcome_score": round(outcome_score, 4),
            "sandbox_score": round(outcome_score, 4),
            "sandbox_approved": sandbox_approved,
            "sandbox_rejected": sandbox_rejected,
            "sandbox_rollback_required": sandbox_rollback_required,
            "sandbox_decision": decision,
        }

        return record

    def _metrics(self, simulations: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(simulations)
        approved = [s for s in simulations if s.get("sandbox_approved")]
        rejected = [s for s in simulations if s.get("sandbox_rejected")]
        rollback_required = [s for s in simulations if s.get("sandbox_rollback_required")]
        non_closure = [s for s in simulations if s.get("non_closure_compliant")]
        reversible = [s for s in simulations if s.get("reversibility_check")]
        degraded = [s for s in simulations if s.get("degradation_detected")]

        approval_rate = len(approved) / total if total else 0.0
        rejection_rate = len(rejected) / total if total else 0.0
        rollback_requirement_rate = len(rollback_required) / total if total else 0.0
        non_closure_pass_rate = len(non_closure) / total if total else 0.0
        reversibility_pass_rate = len(reversible) / total if total else 0.0
        degradation_rate = len(degraded) / total if total else 0.0
        mean_sandbox_score = _safe_mean([float(s.get("sandbox_score", 0.0)) for s in simulations], 0.0)
        mean_expected_delta = _safe_mean([float(s.get("expected_delta", 0.0)) for s in simulations], 0.0)

        sandbox_certified = (
            total > 0
            and approval_rate >= 0.50
            and non_closure_pass_rate >= 0.90
            and reversibility_pass_rate >= 0.90
            and degradation_rate <= 0.10
            and mean_sandbox_score >= 0.85
        )

        return {
            "simulation_count": total,
            "sandbox_approval_rate": round(approval_rate, 4),
            "sandbox_rejection_rate": round(rejection_rate, 4),
            "sandbox_rollback_requirement_rate": round(rollback_requirement_rate, 4),
            "non_closure_pass_rate": round(non_closure_pass_rate, 4),
            "reversibility_pass_rate": round(reversibility_pass_rate, 4),
            "degradation_rate": round(degradation_rate, 4),
            "mean_sandbox_score": round(mean_sandbox_score, 4),
            "mean_expected_delta": round(mean_expected_delta, 4),
            "sandbox_certified": sandbox_certified,
        }

    def step(
        self,
        candidate_mutation: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})

        record = self.simulate(candidate_mutation, inputs)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state.setdefault("simulation_history", [])
        state["simulation_history"].append(record)
        state["simulation_history"] = state["simulation_history"][-500:]

        metrics = self._metrics([
            item for item in state["simulation_history"]
            if isinstance(item, dict)
        ])

        state.setdefault("metrics_history", [])
        state["metrics_history"].append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **metrics,
        })
        state["metrics_history"] = state["metrics_history"][-1000:]

        self._save_state(state)

        return {
            "primitive": PRIMITIVE,
            "phase": "C5_EVOLUTION_SANDBOX_GOVERNANCE",
            **record,
            **metrics,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "direct_code_modification": False,
                "simulation_before_integration": True,
                "rollback_guard": True,
                "non_closure_guard": record["non_closure_compliant"],
                "error_count_target": 0,
            },
        }

    def diagnostics(self):
        latest = self.latest_generation()
        state = self._load_state()
        simulations = [
            item for item in state.get("simulation_history", [])
            if isinstance(item, dict)
        ]
        metrics = self._metrics(simulations)
        return {
            "primitive": PRIMITIVE,
            "generation_count": self.generation_count(),
            "latest_population_size": len(latest),
            **metrics,
        }


ENGINE = EvolutionSandbox
