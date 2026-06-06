
from statistics import mean

PRIMITIVE = (
    "distributed_open_ended_pluralistic_evolution"
)

DESCRIPTION = (
    "Distributed open ended pluralistic evolution."
)

DEPENDENCIES = [
    "distributed_historical_mutation",
    "mutational_robustness",
    "trajectory_bifurcation",
    "non_convergent_intelligence_dynamics",
    "distributed_pluralistic_stability",
    "adaptive_civilizational_forgetting",
    "distributed_semantic_recycling",
    "possible_worlds_navigation",
    "open_ended_historical_navigation",
    "evolutionary_diversification",
]


class DistributedOpenEndedPluralisticEvolution:

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

        pluralistic_stability = (
            self._bounded(
                state.get(
                    "distributed_pluralistic_stability_index",
                    0.0,
                )
            )
        )

        historical_mutation = (
            self._bounded(
                state.get(
                    "distributed_historical_mutation_index",
                    0.0,
                )
            )
        )

        mutational_robustness = (
            self._bounded(
                state.get(
                    "mutational_robustness_index",
                    0.0,
                )
            )
        )

        navigation_capacity = (
            self._bounded(
                state.get(
                    "open_ended_historical_navigation_index",
                    0.0,
                )
            )
        )

        semantic_recycling = (
            self._bounded(
                state.get(
                    "semantic_recycling_stability",
                    0.0,
                )
            )
        )

        evolutionary_diversification = (
            self._bounded(
                state.get(
                    "diversification_pressure",
                    0.0,
                )
            )
        )

        future_openness = (
            self._bounded(
                state.get(
                    "future_openness_preservation",
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

        exploratory_mutation_capacity = (
            self._bounded(
                (
                    historical_mutation
                    + mutational_robustness
                    + evolutionary_diversification
                ) / 3.0
            )
        )

        regenerative_creativity_index = (
            self._bounded(
                (
                    semantic_recycling
                    + navigation_capacity
                    + future_openness
                ) / 3.0
            )
        )

        anti_rigidification_capacity = (
            self._bounded(
                (
                    exploratory_mutation_capacity
                    + regenerative_creativity_index
                    + (
                        1.0 - convergence_pressure
                    )
                ) / 3.0
            )
        )

        distributed_open_ended_pluralistic_evolution_index = (
            self._bounded(
                mean(
                    [
                        pluralistic_stability,
                        exploratory_mutation_capacity,
                        regenerative_creativity_index,
                        anti_rigidification_capacity,
                    ]
                )
            )
        )

        if (
            distributed_open_ended_pluralistic_evolution_index
            >= 0.90
        ):

            classification = (
                "fully_open_pluralistic_evolution"
            )

        elif (
            distributed_open_ended_pluralistic_evolution_index
            >= 0.70
        ):

            classification = (
                "stable_open_pluralistic_evolution"
            )

        elif (
            distributed_open_ended_pluralistic_evolution_index
            >= 0.50
        ):

            classification = (
                "fragile_open_pluralistic_evolution"
            )

        else:

            classification = (
                "evolutionary_collapse_risk"
            )

        return {
            "exploratory_mutation_capacity":
                round(
                    exploratory_mutation_capacity,
                    4,
                ),
            "regenerative_creativity_index":
                round(
                    regenerative_creativity_index,
                    4,
                ),
            "anti_rigidification_capacity":
                round(
                    anti_rigidification_capacity,
                    4,
                ),
            "distributed_open_ended_pluralistic_evolution_index":
                round(
                    distributed_open_ended_pluralistic_evolution_index,
                    4,
                ),
            "classification":
                classification,
            "open_pluralistic_evolution_viable":
                (
                    distributed_open_ended_pluralistic_evolution_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
