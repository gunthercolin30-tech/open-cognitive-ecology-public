
from statistics import mean

PRIMITIVE = "civilizational_semantic_drift"

DESCRIPTION = (
    "Civilizational semantic drift."
)

DEPENDENCIES = [
    "distributed_symbolic_ecology",
    "symbolic_fragmentation",
    "shared_symbolic_reference",
    "intersubjective_alignment",
    "evolutionary_drift",
    "structural_attractor",
    "attractor_basin",
]


class CivilizationalSemanticDrift:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def evaluate(
        self,
        lineage_semantics=None,
    ):

        lineage_semantics = (
            lineage_semantics or {}
        )

        lineage_count = len(
            lineage_semantics
        )

        if lineage_count <= 1:

            return {
                "semantic_drift_rate": 0.0,
                "semantic_interoperability": 1.0,
                "symbolic_fragmentation_index": 0.0,
                "semantic_attractor_strength": 1.0,
                "semantic_basin_size": 1.0,
                "civilizational_semantic_drift_index": 0.0,
                "semantic_pluralism_viable": True,
            }

        semantic_keys = set()

        for semantics in (
            lineage_semantics.values()
        ):

            semantic_keys.update(
                semantics.keys()
            )

        overlap_scores = []
        divergence_scores = []

        for key in semantic_keys:

            values = []

            for semantics in (
                lineage_semantics.values()
            ):

                if key in semantics:

                    values.append(
                        str(
                            semantics[key]
                        )
                    )

            if not values:
                continue

            unique_values = len(
                set(values)
            )

            overlap = (
                1.0 / unique_values
            )

            divergence = (
                1.0 - overlap
            )

            overlap_scores.append(
                overlap
            )

            divergence_scores.append(
                divergence
            )

        if overlap_scores:

            semantic_interoperability = (
                self._bounded(
                    mean(overlap_scores)
                )
            )

        else:

            semantic_interoperability = 0.0

        if divergence_scores:

            semantic_drift_rate = (
                self._bounded(
                    mean(
                        divergence_scores
                    )
                )
            )

        else:

            semantic_drift_rate = 0.0

        symbolic_fragmentation_index = (
            self._bounded(
                semantic_drift_rate
                * (
                    1.0
                    - semantic_interoperability
                )
            )
        )

        semantic_attractor_strength = (
            self._bounded(
                (
                    semantic_interoperability
                    + (
                        1.0
                        - symbolic_fragmentation_index
                    )
                ) / 2.0
            )
        )

        semantic_basin_size = (
            self._bounded(
                (
                    semantic_interoperability
                    + semantic_attractor_strength
                ) / 2.0
            )
        )

        civilizational_semantic_drift_index = (
            self._bounded(
                mean(
                    [
                        semantic_drift_rate,
                        symbolic_fragmentation_index,
                        (
                            1.0
                            - semantic_interoperability
                        ),
                    ]
                )
            )
        )

        semantic_pluralism_viable = (
            semantic_interoperability >= 0.20
            and symbolic_fragmentation_index <= 0.80
        )

        return {
            "semantic_drift_rate":
                round(
                    semantic_drift_rate,
                    4,
                ),
            "semantic_interoperability":
                round(
                    semantic_interoperability,
                    4,
                ),
            "symbolic_fragmentation_index":
                round(
                    symbolic_fragmentation_index,
                    4,
                ),
            "semantic_attractor_strength":
                round(
                    semantic_attractor_strength,
                    4,
                ),
            "semantic_basin_size":
                round(
                    semantic_basin_size,
                    4,
                ),
            "civilizational_semantic_drift_index":
                round(
                    civilizational_semantic_drift_index,
                    4,
                ),
            "semantic_pluralism_viable":
                semantic_pluralism_viable,
        }

    def step(
        self,
        lineage_semantics=None,
    ):

        return self.evaluate(
            lineage_semantics
        )
