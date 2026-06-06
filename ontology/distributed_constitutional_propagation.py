from statistics import mean

PRIMITIVE = "distributed_constitutional_propagation"

DESCRIPTION = (
    "Distributed propagation of open constitutional invariants."
)

DEPENDENCIES = [
    "distributed_constitutional_memory",
    "distributed_meta_stability",
    "distributed_reflexive_civilizational_identity",
    "distributed_historical_mutation",
    "genealogical_continuity",
    "heterogeneous_node_coordination",
    "runtime_constitutional_integration",
    "historical_open_endedness",
    "anti_closure_metaconstraint",
]


class DistributedConstitutionalPropagation:

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

        propagation_intensity = (
            self._bounded(
                state.get(
                    "propagation_intensity",
                    0.0,
                )
            )
        )

        distributed_coherence = (
            self._bounded(
                state.get(
                    "distributed_coherence",
                    0.0,
                )
            )
        )

        pluralistic_divergence = (
            self._bounded(
                state.get(
                    "pluralistic_divergence",
                    0.0,
                )
            )
        )

        anti_convergence_capacity = (
            self._bounded(
                state.get(
                    "anti_convergence_capacity",
                    0.0,
                )
            )
        )

        genealogical_continuity = (
            self._bounded(
                state.get(
                    "genealogical_continuity",
                    0.0,
                )
            )
        )

        runtime_compatibility = (
            self._bounded(
                state.get(
                    "runtime_compatibility",
                    0.0,
                )
            )
        )

        topological_fragmentation = (
            self._bounded(
                state.get(
                    "topological_fragmentation",
                    0.0,
                )
            )
        )

        constitutional_rigidity = (
            self._bounded(
                state.get(
                    "constitutional_rigidity",
                    0.0,
                )
            )
        )

        distributed_propagation_viability = (
            self._bounded(
                (
                    propagation_intensity
                    + distributed_coherence
                    + pluralistic_divergence
                    + anti_convergence_capacity
                    + genealogical_continuity
                    + runtime_compatibility
                    + (
                        1.0
                        - topological_fragmentation
                    )
                    + (
                        1.0
                        - constitutional_rigidity
                    )
                ) / 8.0
            )
        )

        open_invariant_transmission = (
            self._bounded(
                (
                    propagation_intensity
                    + anti_convergence_capacity
                    + pluralistic_divergence
                    + (
                        1.0
                        - constitutional_rigidity
                    )
                ) / 4.0
            )
        )

        multi_host_stability = (
            self._bounded(
                (
                    distributed_coherence
                    + runtime_compatibility
                    + genealogical_continuity
                    + (
                        1.0
                        - topological_fragmentation
                    )
                ) / 4.0
            )
        )

        convergence_risk = (
            self._bounded(
                (
                    constitutional_rigidity
                    + (
                        1.0
                        - anti_convergence_capacity
                    )
                    + (
                        1.0
                        - pluralistic_divergence
                    )
                ) / 3.0
            )
        )

        distributed_constitutional_propagation_index = (
            self._bounded(
                mean(
                    [
                        distributed_propagation_viability,
                        open_invariant_transmission,
                        multi_host_stability,
                        (
                            1.0
                            - convergence_risk
                        ),
                    ]
                )
            )
        )

        distributed_constitutional_propagation_viable = (
            distributed_constitutional_propagation_index
            >= 0.60
            and convergence_risk <= 0.50
            and topological_fragmentation <= 0.50
        )

        return {
            "distributed_propagation_viability":
                round(
                    distributed_propagation_viability,
                    4,
                ),
            "open_invariant_transmission":
                round(
                    open_invariant_transmission,
                    4,
                ),
            "multi_host_stability":
                round(
                    multi_host_stability,
                    4,
                ),
            "convergence_risk":
                round(
                    convergence_risk,
                    4,
                ),
            "distributed_constitutional_propagation_index":
                round(
                    (
                        distributed_constitutional_propagation_index
                    ),
                    4,
                ),
            "distributed_constitutional_propagation_viable":
                (
                    distributed_constitutional_propagation_viable
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
