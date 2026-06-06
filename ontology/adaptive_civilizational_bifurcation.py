from statistics import mean

PRIMITIVE = (
    "adaptive_civilizational_bifurcation"
)

DESCRIPTION = (
    "Adaptive civilizational bifurcation."
)

DEPENDENCIES = [
    "bifurcation_process",
    "bifurcation_dynamics",
    "distributed_meta_stability",
    "intergenerational_symbolic_transition",
    "adaptive_civilizational_forgetting",
]


class AdaptiveCivilizationalBifurcation:

    def _bounded(
        self,
        value,
    ):

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

        branching_pressure = (
            self._bounded(
                state.get(
                    "branching_pressure",
                    0.0,
                )
            )
        )

        adaptive_plasticity = (
            self._bounded(
                state.get(
                    "adaptive_plasticity",
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

        symbolic_transition = (
            self._bounded(
                state.get(
                    "intergenerational_symbolic_transition_index",
                    0.0,
                )
            )
        )

        forgetting_pressure = (
            self._bounded(
                state.get(
                    "forgetting_pressure",
                    0.0,
                )
            )
        )

        fragmentation_risk = (
            self._bounded(
                (
                    forgetting_pressure
                    + (
                        1.0
                        - distributed_meta_stability
                    )
                ) / 2.0
            )
        )

        adaptive_divergence_capacity = (
            self._bounded(
                (
                    branching_pressure
                    + adaptive_plasticity
                    + symbolic_transition
                ) / 3.0
            )
        )

        continuity_preservation = (
            self._bounded(
                (
                    distributed_meta_stability
                    + symbolic_transition
                    + (
                        1.0
                        - fragmentation_risk
                    )
                ) / 3.0
            )
        )

        regenerative_bifurcation_potential = (
            self._bounded(
                (
                    adaptive_divergence_capacity
                    + continuity_preservation
                ) / 2.0
            )
        )

        adaptive_civilizational_bifurcation_index = (
            self._bounded(
                mean(
                    [
                        adaptive_divergence_capacity,
                        continuity_preservation,
                        regenerative_bifurcation_potential,
                    ]
                )
            )
        )

        if (
            adaptive_civilizational_bifurcation_index
            >= 0.85
        ):

            classification = (
                "open_civilizational_bifurcation"
            )

        elif (
            adaptive_civilizational_bifurcation_index
            >= 0.65
        ):

            classification = (
                "adaptive_civilizational_bifurcation"
            )

        elif (
            adaptive_civilizational_bifurcation_index
            >= 0.40
        ):

            classification = (
                "fragile_civilizational_bifurcation"
            )

        else:

            classification = (
                "civilizational_fragmentation_risk"
            )

        return {
            "fragmentation_risk":
                round(
                    fragmentation_risk,
                    4,
                ),
            "adaptive_divergence_capacity":
                round(
                    adaptive_divergence_capacity,
                    4,
                ),
            "continuity_preservation":
                round(
                    continuity_preservation,
                    4,
                ),
            "regenerative_bifurcation_potential":
                round(
                    regenerative_bifurcation_potential,
                    4,
                ),
            "adaptive_civilizational_bifurcation_index":
                round(
                    adaptive_civilizational_bifurcation_index,
                    4,
                ),
            "classification":
                classification,
            "bifurcation_viable":
                (
                    adaptive_civilizational_bifurcation_index
                    >= 0.65
                ),
        }

    def step(
        self,
        state=None,
    ):

        return self.evaluate(
            state
        )
