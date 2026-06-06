PRIMITIVE = "historical_constraint_navigation"

DESCRIPTION = (
    "Strategic navigation across constrained historical corridors."
)

DEPENDENCIES = [
    "open_ended_historical_navigation",
    "refined_long_duration_civilizational_resilience",
    "trajectory_strategy_selection",
    "trajectory_horizon_planning",
    "meta_trajectory_navigation",
    "historical_open_endedness",
    "distributed_civilizational_viability",
    "reflexive_civilizational_ecology",
    "attractor_persistence_analyzer",
    "ecological_fatigue_analyzer",
]


class HistoricalConstraintNavigation:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def evaluate_historical_navigation(
        self,
        corridor_viability,
        exhaustion_pressure,
        bifurcation_adaptability,
        historical_constraint_density,
        divergence_preservation,
        attractor_stability,
        reflexive_steering_capacity,
        long_term_navigation_coherence
    ):

        navigation_index = (
            (corridor_viability * 0.18) +
            ((1.0 - exhaustion_pressure) * 0.18) +
            (bifurcation_adaptability * 0.12) +
            ((1.0 - historical_constraint_density) * 0.10) +
            (divergence_preservation * 0.12) +
            (attractor_stability * 0.10) +
            (reflexive_steering_capacity * 0.10) +
            (long_term_navigation_coherence * 0.10)
        )

        navigation_index = self._bounded(
            navigation_index
        )

        exhaustion_avoidance_capacity = (
            (
                (1.0 - exhaustion_pressure)
                + attractor_stability
                + corridor_viability
            ) / 3.0
        )

        strategic_corridor_selection = (
            (
                corridor_viability
                + reflexive_steering_capacity
                + long_term_navigation_coherence
            ) / 3.0
        )

        constrained_divergence_preservation = (
            (
                divergence_preservation
                + bifurcation_adaptability
                + (1.0 - historical_constraint_density)
            ) / 3.0
        )

        if navigation_index >= 0.75:
            state = (
                "strategically_navigable_historical_regime"
            )
        elif navigation_index >= 0.45:
            state = (
                "fragile_historical_navigation"
            )
        else:
            state = (
                "exhaustion_locked_historical_regime"
            )

        return {
            "historical_navigation_index":
                round(navigation_index, 4),

            "exhaustion_avoidance_capacity":
                round(
                    exhaustion_avoidance_capacity,
                    4
                ),

            "strategic_corridor_selection":
                round(
                    strategic_corridor_selection,
                    4
                ),

            "constrained_divergence_preservation":
                round(
                    constrained_divergence_preservation,
                    4
                ),

            "navigation_state":
                state
        }
