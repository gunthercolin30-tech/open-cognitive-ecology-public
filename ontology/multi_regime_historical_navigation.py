PRIMITIVE = "multi_regime_historical_navigation"

DESCRIPTION = (
    "Navigation and orchestration across multiple historical regimes."
)

DEPENDENCIES = [
    "historical_constraint_navigation",
    "open_ended_historical_navigation",
    "meta_trajectory_navigation",
    "trajectory_horizon_planning",
    "trajectory_strategy_selection",
    "adaptive_civilizational_bifurcation",
    "distributed_meta_stability",
    "ecological_fatigue_analyzer",
    "attractor_persistence_analyzer",
]


class MultiRegimeHistoricalNavigation:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def evaluate_multi_regime_navigation(
        self,
        regime_diversity,
        inter_regime_coherence,
        adaptive_transition_capacity,
        corridor_synchronization,
        attractor_compensation,
        exhaustion_distribution_balance,
        distributed_navigation_capacity,
        long_term_regime_viability
    ):

        navigation_index = (
            (regime_diversity * 0.15) +
            (inter_regime_coherence * 0.15) +
            (adaptive_transition_capacity * 0.15) +
            (corridor_synchronization * 0.15) +
            (attractor_compensation * 0.10) +
            ((1.0 - exhaustion_distribution_balance) * 0.10) +
            (distributed_navigation_capacity * 0.10) +
            (long_term_regime_viability * 0.10)
        )

        navigation_index = self._bounded(
            navigation_index
        )

        regime_synchronization_capacity = (
            (
                inter_regime_coherence
                + corridor_synchronization
                + adaptive_transition_capacity
            ) / 3.0
        )

        distributed_historical_balance = (
            (
                regime_diversity
                + distributed_navigation_capacity
                + (1.0 - exhaustion_distribution_balance)
            ) / 3.0
        )

        attractor_governance_capacity = (
            (
                attractor_compensation
                + long_term_regime_viability
                + inter_regime_coherence
            ) / 3.0
        )

        if navigation_index >= 0.75:
            state = (
                "multi_regime_historically_navigable"
            )
        elif navigation_index >= 0.45:
            state = (
                "fragile_multi_regime_navigation"
            )
        else:
            state = (
                "fragmented_historical_regime_lock"
            )

        return {
            "multi_regime_navigation_index":
                round(navigation_index, 4),

            "regime_synchronization_capacity":
                round(
                    regime_synchronization_capacity,
                    4
                ),

            "distributed_historical_balance":
                round(
                    distributed_historical_balance,
                    4
                ),

            "attractor_governance_capacity":
                round(
                    attractor_governance_capacity,
                    4
                ),

            "navigation_state":
                state
        }
