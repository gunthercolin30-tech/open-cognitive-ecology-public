from __future__ import annotations

from statistics import mean

PRIMITIVE = "distributed_topological_self_adaptation"

DEPENDENCIES = [
    "latent_topological_instability",
    "structural_anomaly_detection",
    "trajectory_adaptation",
    "trajectory_navigation",
    "trajectory_resilience",
    "trajectory_recovery",
    "meta_trajectory_navigation",
    "viability_domain",
    "navigability",
    "open_ended_historical_navigation",
    "historical_constraint_navigation",
    "exploration_exploitation_balance",
    "adaptive_priority_rebalancer",
    "open_epistemic_self_governance",
    "reflective_policy_adjustment",
    "distributed_meta_stability",
    "distributed_semantic_pluralism",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DistributedTopologicalSelfAdaptation:

    def __init__(
        self,
        anti_terminal_threshold: float = 0.65,
        convergence_limit: float = 0.70,
    ):
        self.anti_terminal_threshold = (
            anti_terminal_threshold
        )

        self.convergence_limit = (
            convergence_limit
        )

        self.history = []

    def step(self, state=None):

        state = state or {}

        latent_instability = _bounded(
            state.get(
                "latent_instability",
                0.0,
            )
        )

        future_space_contraction = _bounded(
            state.get(
                "future_space_contraction",
                0.0,
            )
        )

        navigation_capacity = _bounded(
            state.get(
                "navigation_capacity",
                0.0,
            )
        )

        trajectory_diversity = _bounded(
            state.get(
                "trajectory_diversity",
                0.0,
            )
        )

        distributed_meta_stability = _bounded(
            state.get(
                "distributed_meta_stability",
                0.0,
            )
        )

        epistemic_pluralism = _bounded(
            state.get(
                "epistemic_pluralism",
                0.0,
            )
        )

        convergence_pressure = _bounded(
            state.get(
                "convergence_pressure",
                0.0,
            )
        )

        exploration_bias = _bounded(
            state.get(
                "exploration_bias",
                0.0,
            )
        )

        exploitation_bias = _bounded(
            state.get(
                "exploitation_bias",
                0.0,
            )
        )

        adaptive_rigidity = _bounded(
            state.get(
                "adaptive_rigidity",
                0.0,
            )
        )

        historical_constraint_density = _bounded(
            state.get(
                "historical_constraint_density",
                0.0,
            )
        )

        path_guidance = _bounded(
            state.get(
                "path_guidance",
                0.0,
            )
        )

        trajectory_stability = _bounded(
            state.get(
                "trajectory_stability",
                0.0,
            )
        )

        decision_resolution = _bounded(
            state.get(
                "decision_resolution",
                0.0,
            )
        )

        navigability_index = _bounded(
            mean(
                [
                    path_guidance,
                    trajectory_stability,
                    decision_resolution,
                ]
            )
        )

        distributed_adaptation_capacity = _bounded(
            mean(
                [
                    navigation_capacity,
                    trajectory_diversity,
                    distributed_meta_stability,
                    epistemic_pluralism,
                    exploration_bias,
                    navigability_index,
                ]
            )
        )

        anti_terminal_adaptation = _bounded(
            mean(
                [
                    trajectory_diversity,
                    epistemic_pluralism,
                    exploration_bias,
                    1.0 - convergence_pressure,
                    1.0 - adaptive_rigidity,
                ]
            )
        )

        adaptive_closure_risk = _bounded(
            mean(
                [
                    future_space_contraction,
                    convergence_pressure,
                    exploitation_bias,
                    adaptive_rigidity,
                    historical_constraint_density,
                ]
            )
        )

        adaptive_breathing_capacity = _bounded(
            mean(
                [
                    exploration_bias,
                    trajectory_diversity,
                    distributed_meta_stability,
                    1.0 - exploitation_bias,
                ]
            )
        )

        adaptation_viability = _bounded(
            mean(
                [
                    distributed_adaptation_capacity,
                    anti_terminal_adaptation,
                    adaptive_breathing_capacity,
                    1.0 - adaptive_closure_risk,
                ]
            )
        )

        if (
            adaptive_closure_risk
            >= self.convergence_limit
        ):

            classification = (
                "adaptive_closure_risk"
            )

        elif (
            anti_terminal_adaptation
            >= self.anti_terminal_threshold
        ):

            classification = (
                "distributed_open_adaptation"
            )

        else:

            classification = (
                "transitional_distributed_adaptation"
            )

        self.history.append({
            "classification": classification,
            "adaptation_viability":
                adaptation_viability,
        })

        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        return {
            "primitive": PRIMITIVE,
            "classification":
                classification,
            "distributed_adaptation_capacity":
                round(
                    distributed_adaptation_capacity,
                    4,
                ),
            "anti_terminal_adaptation":
                round(
                    anti_terminal_adaptation,
                    4,
                ),
            "adaptive_closure_risk":
                round(
                    adaptive_closure_risk,
                    4,
                ),
            "adaptive_breathing_capacity":
                round(
                    adaptive_breathing_capacity,
                    4,
                ),
            "adaptation_viability":
                round(
                    adaptation_viability,
                    4,
                ),
            "navigability_index":
                round(
                    navigability_index,
                    4,
                ),
            "adaptation_viable":
                adaptation_viability >= 0.60,
            "future_openness_preserved":
                anti_terminal_adaptation >= 0.60,
            "history_size":
                len(self.history),
        }
