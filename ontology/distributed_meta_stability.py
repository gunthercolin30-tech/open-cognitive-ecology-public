from statistics import mean

PRIMITIVE = "distributed_meta_stability"

DESCRIPTION = (
    "Distributed meta stability."
)

DEPENDENCIES = [
    "trajectory_metastability",
    "distributed_historical_mutation",
    "civilizational_semantic_drift",
    "historical_open_endedness",
    "adaptive_ecological_regulation_engine",
]


class DistributedMetaStability:

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
        state=None,
    ):

        state = state or {}

        metastability = self._bounded(
            state.get(
                "trajectory_metastability",
                0.0,
            )
        )

        distributed_mutation = self._bounded(
            state.get(
                "distributed_historical_mutation_index",
                0.0,
            )
        )

        semantic_drift = self._bounded(
            state.get(
                "civilizational_semantic_drift_index",
                0.0,
            )
        )

        historical_openedness = self._bounded(
            state.get(
                "historical_open_endedness_index",
                0.0,
            )
        )

        adaptive_regulation = self._bounded(
            state.get(
                "prospective_stabilization_index",
                0.0,
            )
        )

        anti_rigidity_capacity = (
            self._bounded(
                (
                    semantic_drift
                    + historical_openedness
                    + distributed_mutation
                ) / 3.0
            )
        )

        distributed_coherence = (
            self._bounded(
                (
                    metastability
                    + adaptive_regulation
                    + (
                        1.0
                        - semantic_drift
                    )
                ) / 3.0
            )
        )

        open_stability_index = (
            self._bounded(
                mean(
                    [
                        metastability,
                        distributed_mutation,
                        historical_openedness,
                        adaptive_regulation,
                        distributed_coherence,
                        anti_rigidity_capacity,
                    ]
                )
            )
        )

        distributed_meta_stable = (
            open_stability_index >= 0.70
        )

        if open_stability_index >= 0.90:

            classification = (
                "highly_open_meta_stable"
            )

        elif open_stability_index >= 0.70:

            classification = (
                "distributed_open_meta_stable"
            )

        elif open_stability_index >= 0.50:

            classification = (
                "fragile_meta_stability"
            )

        else:

            classification = (
                "meta_instability_risk"
            )

        return {
            "anti_rigidity_capacity":
                round(
                    anti_rigidity_capacity,
                    4,
                ),
            "distributed_coherence":
                round(
                    distributed_coherence,
                    4,
                ),
            "open_stability_index":
                round(
                    open_stability_index,
                    4,
                ),
            "distributed_meta_stable":
                distributed_meta_stable,
            "classification":
                classification,
        }

    def step(
        self,
        state=None,
    ):

        return self.evaluate(
            state
        )
