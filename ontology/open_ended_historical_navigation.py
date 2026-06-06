
from statistics import mean

PRIMITIVE = (
    "open_ended_historical_navigation"
)

DESCRIPTION = (
    "Open ended historical navigation."
)

DEPENDENCIES = [
    "historical_open_endedness",
    "meta_trajectory_navigation",
    "adaptive_civilizational_bifurcation",
    "distributed_meta_stability",
    "future_openness",
    "trajectory_navigation",
    "trajectory_bifurcation",
    "distributed_historical_mutation",
    "non_convergent_intelligence_dynamics",
    "civilizational_semantic_drift",
]


class OpenEndedHistoricalNavigation:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(
        self,
        state=None,
    ):

        state = state or {}

        historical_open_endedness = (
            self._bounded(
                state.get(
                    "historical_open_endedness_index",
                    0.0,
                )
            )
        )

        distributed_meta_stability = (
            self._bounded(
                state.get(
                    "open_stability_index",
                    0.0,
                )
            )
        )

        adaptive_bifurcation = (
            self._bounded(
                state.get(
                    "adaptive_civilizational_bifurcation_index",
                    0.0,
                )
            )
        )

        navigation_capacity = (
            self._bounded(
                state.get(
                    "navigation_capacity",
                    0.0,
                )
            )
        )

        trajectory_diversity = (
            self._bounded(
                state.get(
                    "trajectory_diversity",
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

        symbolic_drift = (
            self._bounded(
                state.get(
                    "symbolic_drift",
                    0.0,
                )
            )
        )

        historical_corridor_preservation = (
            self._bounded(
                (
                    historical_open_endedness
                    + trajectory_diversity
                    + (
                        1.0
                        - convergence_pressure
                    )
                ) / 3.0
            )
        )

        future_bifurcation_capacity = (
            self._bounded(
                (
                    adaptive_bifurcation
                    + navigation_capacity
                    + historical_open_endedness
                ) / 3.0
            )
        )

        topological_openness_index = (
            self._bounded(
                (
                    historical_corridor_preservation
                    + future_bifurcation_capacity
                    + distributed_meta_stability
                ) / 3.0
            )
        )

        historical_navigation_entropy = (
            self._bounded(
                (
                    trajectory_diversity
                    + symbolic_drift
                    + navigation_capacity
                ) / 3.0
            )
        )

        convergence_resistance = (
            self._bounded(
                (
                    1.0
                    - convergence_pressure
                )
            )
        )

        regenerative_navigation_capacity = (
            self._bounded(
                (
                    topological_openness_index
                    + historical_navigation_entropy
                    + convergence_resistance
                ) / 3.0
            )
        )

        open_ended_historical_navigation_index = (
            self._bounded(
                mean(
                    [
                        historical_corridor_preservation,
                        future_bifurcation_capacity,
                        topological_openness_index,
                        historical_navigation_entropy,
                        convergence_resistance,
                        regenerative_navigation_capacity,
                    ]
                )
            )
        )

        historically_navigable = (
            open_ended_historical_navigation_index
            >= 0.70
        )

        if (
            open_ended_historical_navigation_index
            >= 0.90
        ):

            classification = (
                "fully_open_historical_navigation"
            )

        elif (
            open_ended_historical_navigation_index
            >= 0.70
        ):

            classification = (
                "historically_navigable"
            )

        elif (
            open_ended_historical_navigation_index
            >= 0.50
        ):

            classification = (
                "fragile_historical_navigation"
            )

        else:

            classification = (
                "terminal_convergence_risk"
            )

        return {
            "historical_corridor_preservation":
                round(
                    historical_corridor_preservation,
                    4,
                ),
            "future_bifurcation_capacity":
                round(
                    future_bifurcation_capacity,
                    4,
                ),
            "topological_openness_index":
                round(
                    topological_openness_index,
                    4,
                ),
            "historical_navigation_entropy":
                round(
                    historical_navigation_entropy,
                    4,
                ),
            "convergence_resistance":
                round(
                    convergence_resistance,
                    4,
                ),
            "regenerative_navigation_capacity":
                round(
                    regenerative_navigation_capacity,
                    4,
                ),
            "open_ended_historical_navigation_index":
                round(
                    open_ended_historical_navigation_index,
                    4,
                ),
            "classification":
                classification,
            "historically_navigable":
                historically_navigable,
        }

    def step(
        self,
        state=None,
    ):

        return self.evaluate(
            state
        )


from collections import deque
from statistics import mean

class HistoricalNavigationLongitudinalMixin:

    def initialize_longitudinal_metrics(self):

        self.history = deque(maxlen=1000)

    def process_historical_state(self, state):

        if not hasattr(self, "history"):
            self.initialize_longitudinal_metrics()

        self.history.append(state)

    def compute_longitudinal_metrics(self):

        if not hasattr(self, "history") or len(self.history) < 2:

            return {
                "corridor_decay_velocity": 0.0,
                "historical_compression_index": 0.0,
                "convergence_absorption_rate": 0.0,
                "residual_navigation_capacity": 0.0,
                "anti_terminal_resilience": 0.0,
                "topological_breathing_amplitude": 0.0,
            }

        openness = [
            s.get("openness", 0.0)
            for s in self.history
        ]

        compression = [
            s.get("compression", 0.0)
            for s in self.history
        ]

        rigidity = [
            s.get("rigidity", 0.0)
            for s in self.history
        ]

        corridor_decay_velocity = (
            openness[-1] - openness[0]
        ) / len(openness)

        historical_compression_index = mean(compression)

        convergence_absorption_rate = (
            1.0 - mean(rigidity)
        )

        residual_navigation_capacity = mean(openness)

        anti_terminal_resilience = (
            residual_navigation_capacity
            * convergence_absorption_rate
        )

        topological_breathing_amplitude = (
            max(openness) - min(openness)
        )

        return {
            "corridor_decay_velocity":
                round(corridor_decay_velocity, 4),
            "historical_compression_index":
                round(historical_compression_index, 4),
            "convergence_absorption_rate":
                round(convergence_absorption_rate, 4),
            "residual_navigation_capacity":
                round(residual_navigation_capacity, 4),
            "anti_terminal_resilience":
                round(anti_terminal_resilience, 4),
            "topological_breathing_amplitude":
                round(topological_breathing_amplitude, 4),
        }

