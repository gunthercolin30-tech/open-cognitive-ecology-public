from statistics import mean

PRIMITIVE = "distributed_self_description_field"

DESCRIPTION = (
    "Distributed self description field."
)

DEPENDENCIES = [
    "incomplete_self_representation",
    "distributed_symbolic_ecology",
    "civilizational_semantic_drift",
    "shared_symbolic_reference",
    "symbolic_fragmentation",
    "intersubjective_alignment",
    "distributed_civilizational_memory",
    "trajectory_synchronization",
    "civilizational_meta_governance",
    "anti_closure_metaconstraint",
    "genealogical_continuity",
]


class DistributedSelfDescriptionField:

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
        lineage_descriptions=None,
        shared_reference_strength=0.5,
        fragmentation_pressure=0.5,
        intersubjective_alignment=0.5,
        closure_pressure=0.1,
    ):

        lineage_descriptions = (
            lineage_descriptions or []
        )

        lineage_count = len(
            lineage_descriptions
        )

        if lineage_count == 0:

            return {
                "distributed_description_diversity": 0.0,
                "mutual_intelligibility": 0.0,
                "representational_centralization_risk": 1.0,
                "distributed_self_description_index": 0.0,
                "distributed_reflexivity_viable": False,
            }

        divergence_levels = []
        incompleteness_levels = []

        for description in lineage_descriptions:

            divergence_levels.append(
                self._bounded(
                    description.get(
                        "divergence",
                        0.5,
                    )
                )
            )

            incompleteness_levels.append(
                self._bounded(
                    description.get(
                        "incompleteness",
                        0.5,
                    )
                )
            )

        distributed_description_diversity = (
            self._bounded(
                mean(divergence_levels)
            )
        )

        residual_incompleteness = (
            self._bounded(
                mean(incompleteness_levels)
            )
        )

        shared_reference_strength = (
            self._bounded(
                shared_reference_strength
            )
        )

        fragmentation_pressure = (
            self._bounded(
                fragmentation_pressure
            )
        )

        intersubjective_alignment = (
            self._bounded(
                intersubjective_alignment
            )
        )

        closure_pressure = (
            self._bounded(
                closure_pressure
            )
        )

        mutual_intelligibility = (
            self._bounded(
                (
                    shared_reference_strength
                    + intersubjective_alignment
                    + (
                        1.0
                        - fragmentation_pressure
                    )
                ) / 3.0
            )
        )

        representational_centralization_risk = (
            self._bounded(
                (
                    mutual_intelligibility
                    + (
                        1.0
                        - distributed_description_diversity
                    )
                    + (
                        1.0
                        - residual_incompleteness
                    )
                    + closure_pressure
                ) / 4.0
            )
        )

        distributed_self_description_index = (
            self._bounded(
                mean(
                    [
                        distributed_description_diversity,
                        residual_incompleteness,
                        mutual_intelligibility,
                        (
                            1.0
                            - representational_centralization_risk
                        ),
                    ]
                )
            )
        )

        distributed_reflexivity_viable = (
            distributed_self_description_index >= 0.60
            and representational_centralization_risk <= 0.70
        )

        return {
            "lineage_count":
                lineage_count,
            "distributed_description_diversity":
                round(
                    distributed_description_diversity,
                    4,
                ),
            "residual_incompleteness":
                round(
                    residual_incompleteness,
                    4,
                ),
            "mutual_intelligibility":
                round(
                    mutual_intelligibility,
                    4,
                ),
            "representational_centralization_risk":
                round(
                    representational_centralization_risk,
                    4,
                ),
            "distributed_self_description_index":
                round(
                    distributed_self_description_index,
                    4,
                ),
            "distributed_reflexivity_viable":
                distributed_reflexivity_viable,
        }
