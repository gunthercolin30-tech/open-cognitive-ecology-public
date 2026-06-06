
from statistics import mean

PRIMITIVE = "asynchronous_history_navigation"

DEPENDENCIES = [
    "distributed_historical_branching",
    "real_multi_machine_historical_divergence",
    "trajectory_synchronization",
    "trajectory_coordination",
    "trajectory_metastability",
    "distributed_runtime_coordination",
    "distributed_runtime_coordinator",
    "distributed_civilizational_runtime",
    "distributed_attractor_speciation",
    "future_openness",
    "historical_open_endedness",
    "anti_closure_metaconstraint",
]


class AsynchronousHistoryNavigation:

    def _bounded(self, value):

        return max(0.0, min(1.0, float(value)))

    def evaluate(self, state=None):

        state = state or {}

        asynchronous_divergence = self._bounded(
            state.get(
                "asynchronous_divergence",
                0.0,
            )
        )

        interoperability = self._bounded(
            state.get(
                "interoperability",
                0.0,
            )
        )

        metastability = self._bounded(
            state.get(
                "metastability",
                0.0,
            )
        )

        synchronization_pressure = self._bounded(
            state.get(
                "synchronization_pressure",
                0.0,
            )
        )

        historical_navigation_capacity = self._bounded(
            state.get(
                "historical_navigation_capacity",
                0.0,
            )
        )

        attractor_pluralism = self._bounded(
            state.get(
                "attractor_pluralism",
                0.0,
            )
        )

        historical_openness = self._bounded(
            state.get(
                "historical_openness",
                0.0,
            )
        )

        asynchronous_resilience = self._bounded(
            (
                asynchronous_divergence
                + metastability
                + historical_navigation_capacity
            ) / 3.0
        )

        anti_fusion_navigation = self._bounded(
            (
                attractor_pluralism
                + historical_openness
                + (1.0 - synchronization_pressure)
            ) / 3.0
        )

        inter_history_viability = self._bounded(
            (
                asynchronous_resilience
                + anti_fusion_navigation
                + interoperability
            ) / 3.0
        )

        asynchronous_history_navigation_index = (
            self._bounded(
                mean([
                    asynchronous_resilience,
                    anti_fusion_navigation,
                    inter_history_viability,
                ])
            )
        )

        if (
            synchronization_pressure >= 0.90
            and asynchronous_divergence <= 0.25
        ):

            classification = (
                "terminal_history_synchronization_risk"
            )

        elif (
            asynchronous_history_navigation_index
            >= 0.90
        ):

            classification = (
                "fully_pluralistic_history_navigation"
            )

        elif (
            asynchronous_history_navigation_index
            >= 0.70
        ):

            classification = (
                "stable_asynchronous_history_navigation"
            )

        elif (
            asynchronous_history_navigation_index
            >= 0.50
        ):

            classification = (
                "fragile_asynchronous_history_navigation"
            )

        else:

            classification = (
                "inter_history_navigation_instability"
            )

        return {
            "asynchronous_resilience":
                round(asynchronous_resilience, 4),
            "anti_fusion_navigation":
                round(anti_fusion_navigation, 4),
            "inter_history_viability":
                round(inter_history_viability, 4),
            "asynchronous_history_navigation_index":
                round(
                    asynchronous_history_navigation_index,
                    4,
                ),
            "classification":
                classification,
            "asynchronous_navigation_viable":
                (
                    asynchronous_history_navigation_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
