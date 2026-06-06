
from statistics import mean, pstdev

from ontology.scientific_meta_analysis_engine import (
    ScientificMetaAnalysisEngine
)


class AttractorPersistenceAnalyzer:

    def __init__(self):

        self.meta_analysis_engine = (
            ScientificMetaAnalysisEngine()
        )

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def _safe_stats(self, values):

        if not values:
            return {
                "mean": 0.0,
                "std_dev": 1.0,
            }

        if len(values) == 1:
            return {
                "mean": values[0],
                "std_dev": 0.0,
            }

        return {
            "mean": mean(values),
            "std_dev": pstdev(values),
        }

    def _transition_frequency(
        self,
        values,
        threshold=0.10,
    ):

        if len(values) < 2:
            return 0.0

        transitions = 0

        for i in range(1, len(values)):

            delta = abs(
                values[i]
                - values[i - 1]
            )

            if delta >= threshold:
                transitions += 1

        return transitions / (len(values) - 1)

    def step(self, runs):

        if not runs:
            return {
                "success": False,
                "reason": "no_runs",
            }

        attractor_values = [
            float(
                r.get(
                    "attractor_stability_index",
                    0.0,
                )
            )
            for r in runs
        ]

        coherence_values = [
            float(
                r.get(
                    "trajectory_coherence",
                    0.0,
                )
            )
            for r in runs
        ]

        resilience_values = [
            float(
                r.get(
                    "recovery_resilience_index",
                    0.0,
                )
            )
            for r in runs
        ]

        persistence_stats = self._safe_stats(
            attractor_values
        )

        coherence_stats = self._safe_stats(
            coherence_values
        )

        resilience_stats = self._safe_stats(
            resilience_values
        )

        variability = self._bounded(
            (
                persistence_stats["std_dev"]
                + coherence_stats["std_dev"]
                + resilience_stats["std_dev"]
            ) / 3.0
        )

        attractor_persistence_score = (
            self._bounded(
                persistence_stats["mean"]
                * (1.0 - variability)
            )
        )

        trajectory_convergence_score = (
            self._bounded(
                coherence_stats["mean"]
                * resilience_stats["mean"]
            )
        )

        bifurcation_frequency = (
            self._transition_frequency(
                attractor_values
            )
        )

        basin_stability_index = (
            self._bounded(
                (
                    attractor_persistence_score
                    + trajectory_convergence_score
                    + (
                        1.0
                        - bifurcation_frequency
                    )
                ) / 3.0
            )
        )

        studies = []

        for value in attractor_values:

            studies.append(
                {
                    "effect_size": value,
                    "variance": max(
                        variability,
                        1e-6,
                    ),
                }
            )

        meta_analysis = (
            self.meta_analysis_engine.step(
                studies
            )
        )

        if basin_stability_index >= 0.90:

            attractor_class = (
                "persistent_open_attractor"
            )

        elif basin_stability_index >= 0.75:

            attractor_class = (
                "functional_stable_attractor"
            )

        else:

            attractor_class = (
                "unstable_or_transitional"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "attractor_persistence_score":
                round(
                    attractor_persistence_score,
                    4,
                ),
            "trajectory_convergence_score":
                round(
                    trajectory_convergence_score,
                    4,
                ),
            "bifurcation_frequency":
                round(
                    bifurcation_frequency,
                    4,
                ),
            "basin_stability_index":
                round(
                    basin_stability_index,
                    4,
                ),
            "variability":
                round(
                    variability,
                    4,
                ),
            "attractor_class":
                attractor_class,
            "meta_analysis":
                meta_analysis,
        }
