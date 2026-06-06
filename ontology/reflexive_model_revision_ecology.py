from statistics import mean

PRIMITIVE = "reflexive_model_revision_ecology"

DESCRIPTION = (
    "Reflexive model revision ecology."
)

DEPENDENCIES = [
    "self_model_revision",
    "scientific_self_revision_controller",
    "meta_theoretical_reflexivity",
    "distributed_self_description_field",
    "civilizational_semantic_drift",
    "symbolic_fragmentation",
    "distributed_symbolic_ecology",
    "historical_open_endedness",
    "distributed_historical_mutation",
    "trajectory_synchronization",
    "genealogical_continuity",
    "civilizational_meta_governance",
    "meta_governance_council",
    "anti_closure_metaconstraint",
]


class ReflexiveModelRevisionEcology:

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
        revision_ecosystem=None,
        consensus_pressure=0.2,
        closure_pressure=0.1,
    ):

        revision_ecosystem = (
            revision_ecosystem or []
        )

        revision_count = len(
            revision_ecosystem
        )

        if revision_count == 0:

            return {
                "revision_pluralism": 0.0,
                "revision_openness": 0.0,
                "revision_hegemony_risk": 1.0,
                "reflexive_revision_ecology_index": 0.0,
                "distributed_revision_viable": False,
            }

        divergence_levels = []
        openness_levels = []
        propagation_levels = []

        for revision in revision_ecosystem:

            divergence_levels.append(
                max(
                    0.0,
                    min(
                        1.0,
                        float(
                            revision.get(
                                "revision_divergence",
                                0.5,
                            )
                        ),
                    ),
                )
            )

            openness_levels.append(
                max(
                    0.0,
                    min(
                        1.0,
                        float(
                            revision.get(
                                "revision_openness",
                                0.5,
                            )
                        ),
                    ),
                )
            )

            propagation_levels.append(
                max(
                    0.0,
                    min(
                        1.0,
                        float(
                            revision.get(
                                "propagation_strength",
                                0.5,
                            )
                        ),
                    ),
                )
            )

        revision_pluralism = max(
            0.0,
            min(
                1.0,
                mean(divergence_levels),
            ),
        )

        revision_openness = max(
            0.0,
            min(
                1.0,
                mean(openness_levels),
            ),
        )

        propagation_intensity = max(
            0.0,
            min(
                1.0,
                mean(propagation_levels),
            ),
        )

        consensus_pressure = max(
            0.0,
            min(
                1.0,
                float(consensus_pressure),
            ),
        )

        closure_pressure = max(
            0.0,
            min(
                1.0,
                float(closure_pressure),
            ),
        )

        revision_hegemony_risk = max(
            0.0,
            min(
                1.0,
                (
                    propagation_intensity
                    + consensus_pressure
                    + closure_pressure
                    + (
                        1.0
                        - revision_pluralism
                    )
                ) / 4.0,
            ),
        )

        reflexive_revision_ecology_index = max(
            0.0,
            min(
                1.0,
                mean(
                    [
                        revision_pluralism,
                        revision_openness,
                        (
                            1.0
                            - revision_hegemony_risk
                        ),
                    ]
                ),
            ),
        )

        distributed_revision_viable = (
            reflexive_revision_ecology_index >= 0.60
            and revision_hegemony_risk <= 0.70
        )

        return {
            "revision_count":
                revision_count,
            "revision_pluralism":
                round(
                    revision_pluralism,
                    4,
                ),
            "revision_openness":
                round(
                    revision_openness,
                    4,
                ),
            "propagation_intensity":
                round(
                    propagation_intensity,
                    4,
                ),
            "revision_hegemony_risk":
                round(
                    revision_hegemony_risk,
                    4,
                ),
            "reflexive_revision_ecology_index":
                round(
                    reflexive_revision_ecology_index,
                    4,
                ),
            "distributed_revision_viable":
                distributed_revision_viable,
        }
