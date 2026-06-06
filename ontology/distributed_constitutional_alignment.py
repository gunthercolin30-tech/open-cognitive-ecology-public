from statistics import mean

PRIMITIVE = "distributed_constitutional_alignment"

DESCRIPTION = (
    "Minimal distributed constitutional alignment without convergence."
)

DEPENDENCIES = [
    "distributed_constitutional_propagation",
    "distributed_constitutional_memory",
    "distributed_meta_stability",
    "distributed_reflexive_civilizational_identity",
    "constitutional_plasticity",
    "meta_constitutional_revision",
    "heterogeneous_node_coordination",
    "anti_closure_metaconstraint",
]


class DistributedConstitutionalAlignment:

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

        interoperability = (
            self._bounded(
                state.get(
                    "interoperability",
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

        constitutional_plasticity = (
            self._bounded(
                state.get(
                    "constitutional_plasticity",
                    0.0,
                )
            )
        )

        reflective_revisability = (
            self._bounded(
                state.get(
                    "reflective_revisability",
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

        normative_homogenization = (
            self._bounded(
                state.get(
                    "normative_homogenization",
                    0.0,
                )
            )
        )

        minimal_alignment_capacity = (
            self._bounded(
                (
                    interoperability
                    + distributed_coherence
                    + pluralistic_divergence
                    + anti_convergence_capacity
                    + constitutional_plasticity
                    + reflective_revisability
                    + (
                        1.0
                        - topological_fragmentation
                    )
                    + (
                        1.0
                        - normative_homogenization
                    )
                ) / 8.0
            )
        )

        open_compatibility_index = (
            self._bounded(
                (
                    interoperability
                    + anti_convergence_capacity
                    + pluralistic_divergence
                    + reflective_revisability
                ) / 4.0
            )
        )

        distributed_alignment_stability = (
            self._bounded(
                (
                    distributed_coherence
                    + constitutional_plasticity
                    + (
                        1.0
                        - topological_fragmentation
                    )
                ) / 3.0
            )
        )

        convergence_pressure = (
            self._bounded(
                (
                    normative_homogenization
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

        distributed_constitutional_alignment_index = (
            self._bounded(
                mean(
                    [
                        minimal_alignment_capacity,
                        open_compatibility_index,
                        distributed_alignment_stability,
                        (
                            1.0
                            - convergence_pressure
                        ),
                    ]
                )
            )
        )

        distributed_constitutional_alignment_viable = (
            distributed_constitutional_alignment_index
            >= 0.60
            and convergence_pressure <= 0.50
            and topological_fragmentation <= 0.50
        )

        return {
            "minimal_alignment_capacity":
                round(
                    minimal_alignment_capacity,
                    4,
                ),
            "open_compatibility_index":
                round(
                    open_compatibility_index,
                    4,
                ),
            "distributed_alignment_stability":
                round(
                    distributed_alignment_stability,
                    4,
                ),
            "convergence_pressure":
                round(
                    convergence_pressure,
                    4,
                ),
            "distributed_constitutional_alignment_index":
                round(
                    (
                        distributed_constitutional_alignment_index
                    ),
                    4,
                ),
            "distributed_constitutional_alignment_viable":
                (
                    distributed_constitutional_alignment_viable
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
