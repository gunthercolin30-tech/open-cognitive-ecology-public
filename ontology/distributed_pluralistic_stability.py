
from statistics import mean

PRIMITIVE = "distributed_pluralistic_stability"

DESCRIPTION = (
    "Distributed pluralistic stability."
)

DEPENDENCIES = [
    "distributed_meta_stability",
    "social_ecological_resilience",
    "mutational_robustness",
    "open_ended_historical_navigation",
    "distributed_historical_mutation",
    "multi_lineage_topology",
    "long_duration_civilizational_resilience",
    "adaptive_civilizational_forgetting",
    "intergenerational_symbolic_reconstruction",
]


class DistributedPluralisticStability:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state=None):

        state = state or {}

        multi_lineage_topology = self._bounded(
            state.get(
                "multi_lineage_topology_index",
                0.0,
            )
        )

        historical_navigation = self._bounded(
            state.get(
                "open_ended_historical_navigation_index",
                0.0,
            )
        )

        distributed_mutation = self._bounded(
            state.get(
                "distributed_historical_mutation_index",
                0.0,
            )
        )

        meta_stability = self._bounded(
            state.get(
                "open_stability_index",
                0.0,
            )
        )

        social_ecological_resilience = (
            self._bounded(
                state.get(
                    "social_ecological_resilience_index",
                    0.0,
                )
            )
        )

        mutational_robustness = self._bounded(
            state.get(
                "mutational_robustness_index",
                0.0,
            )
        )

        long_duration_resilience = (
            self._bounded(
                state.get(
                    "long_duration_resilience_index",
                    0.0,
                )
            )
        )

        reconstruction_capacity = (
            self._bounded(
                state.get(
                    "intergenerational_reconstruction_index",
                    0.0,
                )
            )
        )

        forgetting_openness = self._bounded(
            state.get(
                "future_openness_preservation",
                0.0,
            )
        )

        convergence_pressure = self._bounded(
            state.get(
                "convergence_pressure",
                0.0,
            )
        )

        pluralistic_resilience = (
            self._bounded(
                (
                    multi_lineage_topology
                    + historical_navigation
                    + meta_stability
                    + (
                        1.0 - convergence_pressure
                    )
                ) / 4.0
            )
        )

        ecological_persistence = (
            self._bounded(
                (
                    social_ecological_resilience
                    + long_duration_resilience
                    + mutational_robustness
                ) / 3.0
            )
        )

        civilizational_continuity = (
            self._bounded(
                (
                    reconstruction_capacity
                    + forgetting_openness
                    + distributed_mutation
                ) / 3.0
            )
        )

        distributed_pluralistic_stability_index = (
            self._bounded(
                mean(
                    [
                        pluralistic_resilience,
                        ecological_persistence,
                        civilizational_continuity,
                    ]
                )
            )
        )

        if (
            distributed_pluralistic_stability_index
            >= 0.90
        ):

            classification = (
                "fully_stable_pluralistic_ecology"
            )

        elif (
            distributed_pluralistic_stability_index
            >= 0.70
        ):

            classification = (
                "stable_pluralistic_civilization"
            )

        elif (
            distributed_pluralistic_stability_index
            >= 0.50
        ):

            classification = (
                "fragile_pluralistic_stability"
            )

        else:

            classification = (
                "pluralistic_collapse_risk"
            )

        return {
            "pluralistic_resilience":
                round(
                    pluralistic_resilience,
                    4,
                ),
            "ecological_persistence":
                round(
                    ecological_persistence,
                    4,
                ),
            "civilizational_continuity":
                round(
                    civilizational_continuity,
                    4,
                ),
            "distributed_pluralistic_stability_index":
                round(
                    distributed_pluralistic_stability_index,
                    4,
                ),
            "classification":
                classification,
            "distributed_pluralistic_stable":
                (
                    distributed_pluralistic_stability_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
