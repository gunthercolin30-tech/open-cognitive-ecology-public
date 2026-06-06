from statistics import mean

PRIMITIVE = (
    "intergenerational_symbolic_transition"
)

DESCRIPTION = (
    "Intergenerational symbolic transition."
)

DEPENDENCIES = [
    "intergenerational_transmission_process",
    "intergenerational_continuity_metrics",
    "distributed_symbolic_ecology",
    "shared_symbolic_reference",
    "symbolic_fragmentation",
    "trajectory_bifurcation",
]


class IntergenerationalSymbolicTransition:

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

        continuity_index = (
            self._bounded(
                state.get(
                    "continuity_index",
                    0.0,
                )
            )
        )

        ecological_stability = (
            self._bounded(
                state.get(
                    "ecological_stability",
                    0.0,
                )
            )
        )

        symbolic_reference = (
            self._bounded(
                state.get(
                    "shared_symbolic_reference_index",
                    0.0,
                )
            )
        )

        symbolic_fragmentation = (
            self._bounded(
                state.get(
                    "fragmentation_pressure",
                    0.0,
                )
            )
        )

        bifurcation_capacity = (
            self._bounded(
                state.get(
                    "bifurcation_capacity",
                    0.0,
                )
            )
        )

        reinterpretation_capacity = (
            self._bounded(
                (
                    symbolic_reference
                    + bifurcation_capacity
                    + (
                        1.0
                        - symbolic_fragmentation
                    )
                ) / 3.0
            )
        )

        transformation_viability = (
            self._bounded(
                (
                    continuity_index
                    + ecological_stability
                    + reinterpretation_capacity
                ) / 3.0
            )
        )

        non_rigid_continuity = (
            self._bounded(
                (
                    transformation_viability
                    + bifurcation_capacity
                    + (
                        1.0
                        - symbolic_fragmentation
                    )
                ) / 3.0
            )
        )

        intergenerational_symbolic_transition_index = (
            self._bounded(
                mean(
                    [
                        reinterpretation_capacity,
                        transformation_viability,
                        non_rigid_continuity,
                    ]
                )
            )
        )

        if (
            intergenerational_symbolic_transition_index
            >= 0.85
        ):

            classification = (
                "open_intergenerational_transition"
            )

        elif (
            intergenerational_symbolic_transition_index
            >= 0.65
        ):

            classification = (
                "adaptive_symbolic_transition"
            )

        elif (
            intergenerational_symbolic_transition_index
            >= 0.40
        ):

            classification = (
                "fragile_symbolic_transition"
            )

        else:

            classification = (
                "intergenerational_fragmentation_risk"
            )

        return {
            "reinterpretation_capacity":
                round(
                    reinterpretation_capacity,
                    4,
                ),
            "transformation_viability":
                round(
                    transformation_viability,
                    4,
                ),
            "non_rigid_continuity":
                round(
                    non_rigid_continuity,
                    4,
                ),
            "intergenerational_symbolic_transition_index":
                round(
                    (
                        intergenerational_symbolic_transition_index
                    ),
                    4,
                ),
            "classification":
                classification,
            "transition_viable":
                (
                    intergenerational_symbolic_transition_index
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
