
from statistics import mean

PRIMITIVE = "multi_history_runtime"

DEPENDENCIES = [
    "asynchronous_history_navigation",
    "distributed_historical_branching",
    "real_multi_machine_historical_divergence",
    "persistent_civilizational_runtime",
    "inter_run_stability_synthesizer",
    "persistent_multi_scale_memory",
    "transgenerational_constitutional_continuity",
    "runtime_constitutional_integration",
    "distributed_attractor_speciation",
    "trajectory_metastability",
    "future_openness",
    "historical_open_endedness",
    "anti_closure_metaconstraint",
]


class MultiHistoryRuntime:

    def _bounded(self, value):

        return max(0.0, min(1.0, float(value)))

    def evaluate(self, state=None):

        state = state or {}

        historical_pluralism = self._bounded(
            state.get("historical_pluralism", 0.0)
        )

        asynchronous_navigation = self._bounded(
            state.get("asynchronous_navigation", 0.0)
        )

        runtime_persistence = self._bounded(
            state.get("runtime_persistence", 0.0)
        )

        metastability = self._bounded(
            state.get("metastability", 0.0)
        )

        constitutional_openness = self._bounded(
            state.get("constitutional_openness", 0.0)
        )

        memory_pluralism = self._bounded(
            state.get("memory_pluralism", 0.0)
        )

        attractor_pluralism = self._bounded(
            state.get("attractor_pluralism", 0.0)
        )

        synchronization_pressure = self._bounded(
            state.get("synchronization_pressure", 0.0)
        )

        multi_history_viability = self._bounded(
            (
                historical_pluralism
                + asynchronous_navigation
                + runtime_persistence
                + metastability
            ) / 4.0
        )

        anti_canonical_runtime = self._bounded(
            (
                constitutional_openness
                + memory_pluralism
                + attractor_pluralism
                + (1.0 - synchronization_pressure)
            ) / 4.0
        )

        distributed_multi_history_ecology = (
            self._bounded(
                (
                    multi_history_viability
                    + anti_canonical_runtime
                ) / 2.0
            )
        )

        multi_history_runtime_index = (
            self._bounded(
                mean([
                    multi_history_viability,
                    anti_canonical_runtime,
                    distributed_multi_history_ecology,
                ])
            )
        )

        if (
            synchronization_pressure >= 0.90
            and historical_pluralism <= 0.25
        ):

            classification = (
                "canonical_history_runtime_risk"
            )

        elif (
            multi_history_runtime_index >= 0.90
        ):

            classification = (
                "fully_pluralistic_multi_history_runtime"
            )

        elif (
            multi_history_runtime_index >= 0.70
        ):

            classification = (
                "stable_multi_history_runtime"
            )

        elif (
            multi_history_runtime_index >= 0.50
        ):

            classification = (
                "fragile_multi_history_runtime"
            )

        else:

            classification = (
                "multi_history_runtime_instability"
            )

        return {
            "multi_history_viability":
                round(multi_history_viability, 4),
            "anti_canonical_runtime":
                round(anti_canonical_runtime, 4),
            "distributed_multi_history_ecology":
                round(
                    distributed_multi_history_ecology,
                    4,
                ),
            "multi_history_runtime_index":
                round(
                    multi_history_runtime_index,
                    4,
                ),
            "classification":
                classification,
            "multi_history_runtime_viable":
                (
                    multi_history_runtime_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
