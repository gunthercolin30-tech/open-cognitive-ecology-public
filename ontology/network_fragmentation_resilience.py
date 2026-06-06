
from statistics import mean

PRIMITIVE = "network_fragmentation_resilience"

DEPENDENCIES = [
    "distributed_civilizational_viability",
    "distributed_meta_stability",
    "trajectory_recovery",
    "longitudinal_recovery_observer",
    "distributed_historical_mutation",
    "symbolic_fragmentation",
    "reflexive_fragmentation_stress_test",
    "trajectory_resilience",
    "trajectory_irreversibility",
    "trajectory_hysteresis",
    "historical_open_endedness",
    "future_openness",
    "anti_closure_metaconstraint",
]


class NetworkFragmentationResilience:

    def _bounded(self, value):

        return max(0.0, min(1.0, float(value)))

    def evaluate(self, state=None):

        state = state or {}

        network_fragmentation = self._bounded(
            state.get("network_fragmentation", 0.0)
        )

        distributed_viability = self._bounded(
            state.get("distributed_viability", 0.0)
        )

        meta_stability = self._bounded(
            state.get("meta_stability", 0.0)
        )

        historical_mutation_pressure = self._bounded(
            state.get(
                "historical_mutation_pressure",
                0.0,
            )
        )

        recovery_capacity = self._bounded(
            state.get("recovery_capacity", 0.0)
        )

        closure_pressure = self._bounded(
            state.get("closure_pressure", 0.0)
        )

        future_openness = self._bounded(
            state.get("future_openness", 0.0)
        )

        fragmentation_tolerance = self._bounded(
            (
                distributed_viability
                + meta_stability
                + recovery_capacity
            ) / 3.0
        )

        anti_terminal_recovery = self._bounded(
            (
                future_openness
                + recovery_capacity
                + (1.0 - closure_pressure)
            ) / 3.0
        )

        resilient_fragmentation_capacity = (
            self._bounded(
                (
                    fragmentation_tolerance
                    + anti_terminal_recovery
                    + (
                        1.0
                        - network_fragmentation
                    )
                ) / 3.0
            )
        )

        network_fragmentation_resilience_index = (
            self._bounded(
                mean([
                    fragmentation_tolerance,
                    anti_terminal_recovery,
                    resilient_fragmentation_capacity,
                ])
            )
        )

        if (
            network_fragmentation >= 0.90
            and recovery_capacity <= 0.30
        ):

            classification = (
                "fragmentation_collapse_risk"
            )

        elif (
            network_fragmentation_resilience_index
            >= 0.70
        ):

            classification = (
                "resilient_fragmented_civilization"
            )

        elif (
            network_fragmentation_resilience_index
            >= 0.50
        ):

            classification = (
                "fragile_fragmented_civilization"
            )

        else:

            classification = (
                "distributed_fragmentation_instability"
            )

        return {
            "fragmentation_tolerance":
                round(fragmentation_tolerance, 4),
            "anti_terminal_recovery":
                round(anti_terminal_recovery, 4),
            "resilient_fragmentation_capacity":
                round(
                    resilient_fragmentation_capacity,
                    4,
                ),
            "network_fragmentation_resilience_index":
                round(
                    network_fragmentation_resilience_index,
                    4,
                ),
            "classification":
                classification,
            "fragmentation_resilience_viable":
                (
                    network_fragmentation_resilience_index
                    >= 0.70
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
