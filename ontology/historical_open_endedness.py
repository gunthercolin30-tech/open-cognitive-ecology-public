
from statistics import mean

PRIMITIVE = "historical_open_endedness"

DESCRIPTION = (
    "Historical open endedness."
)

DEPENDENCIES = [
    "civilizational_historical_archive",
    "open_endedness",
    "future_openness",
    "non_convergent_intelligence_dynamics",
    "bifurcation_dynamics",
    "distributed_symbolic_ecology",
    "adaptive_ecological_regulation_engine",
    "attractor_persistence_analyzer",
    "meta_adaptation",
]


class HistoricalOpenEndedness:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(self, state):

        historical_diversity = (
            self._bounded(
                state.get(
                    "historical_diversity",
                    0.0,
                )
            )
        )

        bifurcation_accessibility = (
            self._bounded(
                state.get(
                    "bifurcation_accessibility",
                    0.0,
                )
            )
        )

        historical_exploration = (
            self._bounded(
                state.get(
                    "historical_exploration",
                    0.0,
                )
            )
        )

        closure_pressure = (
            self._bounded(
                state.get(
                    "closure_pressure",
                    0.0,
                )
            )
        )

        archival_accumulation_pressure = (
            self._bounded(
                state.get(
                    "archival_accumulation_pressure",
                    0.0,
                )
            )
        )

        trajectory_convergence = (
            self._bounded(
                state.get(
                    "trajectory_convergence",
                    0.0,
                )
            )
        )

        historical_non_convergence = (
            self._bounded(
                1.0
                - trajectory_convergence
            )
        )

        anti_fossilization_capacity = (
            self._bounded(
                (
                    historical_diversity
                    + bifurcation_accessibility
                    + historical_exploration
                    + (
                        1.0
                        - closure_pressure
                    )
                    + (
                        1.0
                        - archival_accumulation_pressure
                    )
                    + historical_non_convergence
                ) / 6.0
            )
        )

        bifurcation_openness = (
            self._bounded(
                (
                    bifurcation_accessibility
                    + historical_exploration
                    + historical_non_convergence
                ) / 3.0
            )
        )

        historical_exploration_persistence = (
            self._bounded(
                (
                    historical_exploration
                    + historical_diversity
                    + (
                        1.0
                        - closure_pressure
                    )
                ) / 3.0
            )
        )

        historical_open_endedness_index = (
            self._bounded(
                mean(
                    [
                        anti_fossilization_capacity,
                        bifurcation_openness,
                        historical_exploration_persistence,
                    ]
                )
            )
        )

        historically_open = (
            historical_open_endedness_index >= 0.60
        )

        return {
            "historical_diversity_index":
                round(
                    historical_diversity,
                    4,
                ),
            "historical_non_convergence":
                round(
                    historical_non_convergence,
                    4,
                ),
            "bifurcation_openness":
                round(
                    bifurcation_openness,
                    4,
                ),
            "anti_fossilization_capacity":
                round(
                    anti_fossilization_capacity,
                    4,
                ),
            "historical_exploration_persistence":
                round(
                    historical_exploration_persistence,
                    4,
                ),
            "historical_open_endedness_index":
                round(
                    historical_open_endedness_index,
                    4,
                ),
            "historically_open":
                historically_open,
        }

    def step(self, state):

        return self.evaluate(state)
