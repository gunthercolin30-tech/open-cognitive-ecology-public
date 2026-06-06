from statistics import mean

PRIMITIVE = "constitutional_plasticity"

DESCRIPTION = (
    "Governed constitutional plasticity under openness constraints."
)

DEPENDENCIES = [
    "adaptive_constitutional_evolution",
    "constitutional_integrity_index",
    "distributed_constitutional_memory",
    "distributed_meta_stability",
    "adaptive_civilizational_bifurcation",
    "constitutional_alert_system",
    "anti_closure_metaconstraint",
]


class ConstitutionalPlasticity:

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

        adaptive_capacity = (
            self._bounded(
                state.get(
                    "adaptive_capacity",
                    0.0,
                )
            )
        )

        constitutional_integrity = (
            self._bounded(
                state.get(
                    "constitutional_integrity",
                    0.0,
                )
            )
        )

        distributed_meta_stability = (
            self._bounded(
                state.get(
                    "distributed_meta_stability",
                    0.0,
                )
            )
        )

        revision_openness = (
            self._bounded(
                state.get(
                    "revision_openness",
                    0.0,
                )
            )
        )

        anti_dogmatism = (
            self._bounded(
                state.get(
                    "anti_dogmatism",
                    0.0,
                )
            )
        )

        bifurcation_viability = (
            self._bounded(
                state.get(
                    "bifurcation_viability",
                    0.0,
                )
            )
        )

        normative_rigidity = (
            self._bounded(
                state.get(
                    "normative_rigidity",
                    0.0,
                )
            )
        )

        collapse_risk = (
            self._bounded(
                state.get(
                    "collapse_risk",
                    0.0,
                )
            )
        )

        constitutional_plasticity_index = (
            self._bounded(
                (
                    adaptive_capacity
                    + constitutional_integrity
                    + distributed_meta_stability
                    + revision_openness
                    + anti_dogmatism
                    + bifurcation_viability
                    + (
                        1.0
                        - normative_rigidity
                    )
                    + (
                        1.0
                        - collapse_risk
                    )
                ) / 8.0
            )
        )

        openness_preservation_capacity = (
            self._bounded(
                (
                    revision_openness
                    + anti_dogmatism
                    + (
                        1.0
                        - normative_rigidity
                    )
                ) / 3.0
            )
        )

        destructive_mutation_risk = (
            self._bounded(
                (
                    collapse_risk
                    + normative_rigidity
                    + (
                        1.0
                        - constitutional_integrity
                    )
                    + (
                        1.0
                        - distributed_meta_stability
                    )
                ) / 4.0
            )
        )

        adaptive_constitutional_viability = (
            self._bounded(
                mean(
                    [
                        constitutional_plasticity_index,
                        openness_preservation_capacity,
                        (
                            1.0
                            - destructive_mutation_risk
                        ),
                    ]
                )
            )
        )

        plasticity_viable = (
            adaptive_constitutional_viability >= 0.60
            and destructive_mutation_risk <= 0.50
            and openness_preservation_capacity >= 0.60
        )

        return {
            "constitutional_plasticity_index":
                round(
                    constitutional_plasticity_index,
                    4,
                ),
            "openness_preservation_capacity":
                round(
                    openness_preservation_capacity,
                    4,
                ),
            "destructive_mutation_risk":
                round(
                    destructive_mutation_risk,
                    4,
                ),
            "adaptive_constitutional_viability":
                round(
                    adaptive_constitutional_viability,
                    4,
                ),
            "plasticity_viable":
                plasticity_viable,
        }

    def step(self, state=None):

        return self.evaluate(state)
