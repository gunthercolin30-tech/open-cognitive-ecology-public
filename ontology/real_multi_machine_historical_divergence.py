
from statistics import mean

PRIMITIVE = (
    "real_multi_machine_historical_divergence"
)

DEPENDENCIES = [
    "distributed_historical_mutation",
    "multi_regime_historical_navigation",
    "open_ended_historical_navigation",
    "trajectory_irreversibility",
    "reflexive_identity_hysteresis",
    "civilizational_semantic_drift",
    "trajectory_bifurcation",
    "trajectory_path_dependency",
    "trajectory_hysteresis",
    "distributed_open_ended_pluralistic_evolution",
    "future_openness",
    "historical_open_endedness",
    "anti_closure_metaconstraint",
]


class RealMultiMachineHistoricalDivergence:

    def _bounded(self, value):

        return max(0.0, min(1.0, float(value)))

    def evaluate(self, state=None):

        state = state or {}

        historical_branch_diversity = (
            self._bounded(
                state.get(
                    "historical_branch_diversity",
                    0.0,
                )
            )
        )

        semantic_drift_capacity = (
            self._bounded(
                state.get(
                    "semantic_drift_capacity",
                    0.0,
                )
            )
        )

        interoperability = (
            self._bounded(
                state.get(
                    "interoperability",
                    0.0,
                )
            )
        )

        irreversibility = (
            self._bounded(
                state.get(
                    "irreversibility",
                    0.0,
                )
            )
        )

        historical_openness = (
            self._bounded(
                state.get(
                    "historical_openness",
                    0.0,
                )
            )
        )

        convergence_pressure = (
            self._bounded(
                state.get(
                    "convergence_pressure",
                    0.0,
                )
            )
        )

        distributed_viability = (
            self._bounded(
                state.get(
                    "distributed_viability",
                    0.0,
                )
            )
        )

        divergence_capacity = (
            self._bounded(
                (
                    historical_branch_diversity
                    + semantic_drift_capacity
                    + irreversibility
                ) / 3.0
            )
        )

        open_historical_viability = (
            self._bounded(
                (
                    historical_openness
                    + distributed_viability
                    + (
                        1.0
                        - convergence_pressure
                    )
                ) / 3.0
            )
        )

        multi_history_balance = (
            self._bounded(
                (
                    divergence_capacity
                    + open_historical_viability
                    + interoperability
                ) / 3.0
            )
        )

        real_multi_machine_historical_divergence_index = (
            self._bounded(
                mean([
                    divergence_capacity,
                    open_historical_viability,
                    multi_history_balance,
                ])
            )
        )

        if (
            convergence_pressure >= 0.90
            and historical_branch_diversity <= 0.25
        ):

            classification = (
                "terminal_historical_convergence_risk"
            )

        elif (
            real_multi_machine_historical_divergence_index
            >= 0.70
        ):

            classification = (
                "stable_multi_history_divergence"
            )

        elif (
            real_multi_machine_historical_divergence_index
            >= 0.50
        ):

            classification = (
                "fragile_multi_history_divergence"
            )

        else:

            classification = (
                "historical_fragmentation_instability"
            )

        return {
            "divergence_capacity":
                round(divergence_capacity, 4),
            "open_historical_viability":
                round(open_historical_viability, 4),
            "multi_history_balance":
                round(multi_history_balance, 4),
            "real_multi_machine_historical_divergence_index":
                round(
                    real_multi_machine_historical_divergence_index,
                    4,
                ),
            "classification":
                classification,
            "multi_history_viable":
                (
                    real_multi_machine_historical_divergence_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
