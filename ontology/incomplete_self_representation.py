from statistics import mean

PRIMITIVE = "incomplete_self_representation"

DESCRIPTION = (
    "Incomplete self representation."
)

DEPENDENCIES = [
    "self_model",
    "self_model_revision",
    "theory_of_non_representability",
    "meta_theoretical_reflexivity",
    "distributed_symbolic_ecology",
    "civilizational_semantic_drift",
    "anti_closure_metaconstraint",
    "historical_open_endedness",
]


class IncompleteSelfRepresentation:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def step(
        self,
        self_description_completeness=0.5,
        representational_stability=0.5,
        epistemic_openness=0.5,
        closure_pressure=0.1,
    ):

        self_description_completeness = (
            self._bounded(
                self_description_completeness
            )
        )

        representational_stability = (
            self._bounded(
                representational_stability
            )
        )

        epistemic_openness = (
            self._bounded(
                epistemic_openness
            )
        )

        closure_pressure = (
            self._bounded(
                closure_pressure
            )
        )

        residual_incompleteness = (
            self._bounded(
                1.0
                - self_description_completeness
            )
        )

        anti_totalization_capacity = (
            self._bounded(
                mean(
                    [
                        residual_incompleteness,
                        epistemic_openness,
                        (
                            1.0
                            - representational_stability
                        ),
                        (
                            1.0
                            - closure_pressure
                        ),
                    ]
                )
            )
        )

        representational_rigidity_risk = (
            self._bounded(
                mean(
                    [
                        self_description_completeness,
                        representational_stability,
                        closure_pressure,
                    ]
                )
            )
        )

        open_self_model_viable = (
            anti_totalization_capacity >= 0.60
            and representational_rigidity_risk <= 0.75
        )

        return {
            "residual_incompleteness":
                round(
                    residual_incompleteness,
                    4,
                ),
            "anti_totalization_capacity":
                round(
                    anti_totalization_capacity,
                    4,
                ),
            "representational_rigidity_risk":
                round(
                    representational_rigidity_risk,
                    4,
                ),
            "open_self_model_viable":
                open_self_model_viable,
        }
