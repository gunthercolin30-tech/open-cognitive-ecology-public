from statistics import mean

PRIMITIVE = "distributed_constitutional_memory"

DESCRIPTION = (
    "Distributed constitutional memory."
)

DEPENDENCIES = [
    "open_constitutional_transmission",
    "civilizational_memory",
    "distributed_civilizational_memory",
    "civilizational_memory_archive",
    "distributed_reflexive_civilizational_identity",
    "open_epistemic_self_governance",
    "genealogical_continuity",
    "distributed_historical_mutation",
    "anti_closure_metaconstraint",
]


class DistributedConstitutionalMemory:

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

        constitutional_nodes = (
            state.get(
                "constitutional_nodes",
                []
            )
        )

        if not constitutional_nodes:

            return {
                "distributed_constitutional_memory_viable":
                    False,
                "reason":
                    "no_constitutional_nodes",
            }

        continuity = mean([
            self._bounded(
                n.get(
                    "continuity",
                    0.0,
                )
            )
            for n in constitutional_nodes
        ])

        revision_capacity = mean([
            self._bounded(
                n.get(
                    "revision_capacity",
                    0.0,
                )
            )
            for n in constitutional_nodes
        ])

        anti_dogmatism = mean([
            self._bounded(
                n.get(
                    "anti_dogmatism",
                    0.0,
                )
            )
            for n in constitutional_nodes
        ])

        distributed_openness = mean([
            self._bounded(
                n.get(
                    "distributed_openness",
                    0.0,
                )
            )
            for n in constitutional_nodes
        ])

        fragmentation_pressure = (
            self._bounded(
                state.get(
                    "fragmentation_pressure",
                    0.0,
                )
            )
        )

        canonicalization_pressure = (
            self._bounded(
                state.get(
                    "canonicalization_pressure",
                    0.0,
                )
            )
        )

        memory_rigidity = (
            self._bounded(
                state.get(
                    "memory_rigidity",
                    0.0,
                )
            )
        )

        intergenerational_divergence = (
            self._bounded(
                state.get(
                    "intergenerational_divergence",
                    0.0,
                )
            )
        )

        constitutional_memory_continuity = (
            self._bounded(
                (
                    continuity
                    + revision_capacity
                    + distributed_openness
                ) / 3.0
            )
        )

        constitutional_memory_openness = (
            self._bounded(
                (
                    anti_dogmatism
                    + distributed_openness
                    + revision_capacity
                    + intergenerational_divergence
                    + (
                        1.0
                        - canonicalization_pressure
                    )
                    + (
                        1.0
                        - memory_rigidity
                    )
                ) / 6.0
            )
        )

        canonicalization_risk = (
            self._bounded(
                (
                    canonicalization_pressure
                    + memory_rigidity
                    + (
                        1.0
                        - anti_dogmatism
                    )
                    + (
                        1.0
                        - revision_capacity
                    )
                ) / 4.0
            )
        )

        distributed_constitutional_memory_index = (
            self._bounded(
                mean(
                    [
                        constitutional_memory_continuity,
                        constitutional_memory_openness,
                        (
                            1.0
                            - canonicalization_risk
                        ),
                        (
                            1.0
                            - fragmentation_pressure
                        ),
                    ]
                )
            )
        )

        distributed_constitutional_memory_viable = (
            distributed_constitutional_memory_index >= 0.60
            and constitutional_memory_openness >= 0.60
            and canonicalization_risk <= 0.50
        )

        return {
            "constitutional_memory_continuity":
                round(
                    constitutional_memory_continuity,
                    4,
                ),
            "constitutional_memory_openness":
                round(
                    constitutional_memory_openness,
                    4,
                ),
            "canonicalization_risk":
                round(
                    canonicalization_risk,
                    4,
                ),
            "distributed_constitutional_memory_index":
                round(
                    distributed_constitutional_memory_index,
                    4,
                ),
            "distributed_constitutional_memory_viable":
                (
                    distributed_constitutional_memory_viable
                ),
        }

    def step(self, state=None):

        return self.evaluate(state)
