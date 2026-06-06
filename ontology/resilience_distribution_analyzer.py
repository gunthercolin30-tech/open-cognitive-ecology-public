
from statistics import mean, pstdev

from ontology.scientific_meta_analysis_engine import (
    ScientificMetaAnalysisEngine
)


class ResilienceDistributionAnalyzer:

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

    def _recovery_latency_distribution(
        self,
        values,
        threshold=0.70,
    ):

        latencies = []

        for value in values:

            if value >= threshold:
                latencies.append(1.0)
            else:
                latencies.append(
                    1.0 + (
                        threshold - value
                    )
                )

        return latencies

    def step(self, runs):

        if not runs:
            return {
                "success": False,
                "reason": "no_runs",
            }

        resilience_values = [
            float(
                r.get(
                    "recovery_resilience_index",
                    0.0,
                )
            )
            for r in runs
        ]

        persistence_values = [
            float(
                r.get(
                    "attractor_persistence_score",
                    0.0,
                )
            )
            for r in runs
        ]

        convergence_values = [
            float(
                r.get(
                    "trajectory_convergence_score",
                    0.0,
                )
            )
            for r in runs
        ]

        resilience_stats = self._safe_stats(
            resilience_values
        )

        persistence_stats = self._safe_stats(
            persistence_values
        )

        convergence_stats = self._safe_stats(
            convergence_values
        )

        recovery_latencies = (
            self._recovery_latency_distribution(
                resilience_values
            )
        )

        latency_stats = self._safe_stats(
            recovery_latencies
        )

        resilience_variability = (
            self._bounded(
                resilience_stats["std_dev"]
            )
        )

        resilience_distribution_index = (
            self._bounded(
                (
                    resilience_stats["mean"]
                    + persistence_stats["mean"]
                    + convergence_stats["mean"]
                ) / 3.0
            )
        )

        resilience_recovery_stability = (
            self._bounded(
                1.0
                - latency_stats["std_dev"]
            )
        )

        ecological_recovery_coherence = (
            self._bounded(
                resilience_distribution_index
                * resilience_recovery_stability
            )
        )

        collapse_frequency = 0.0

        if resilience_values:

            collapses = len(
                [
                    v for v in resilience_values
                    if v < 0.4
                ]
            )

            collapse_frequency = (
                collapses / len(resilience_values)
            )

        studies = []

        for value in resilience_values:

            studies.append(
                {
                    "effect_size": value,
                    "variance": max(
                        resilience_variability,
                        1e-6,
                    ),
                }
            )

        meta_analysis = (
            self.meta_analysis_engine.step(
                studies
            )
        )

        if ecological_recovery_coherence >= 0.90:

            resilience_class = (
                "persistent_distributed_resilience"
            )

        elif ecological_recovery_coherence >= 0.75:

            resilience_class = (
                "functional_resilience"
            )

        else:

            resilience_class = (
                "fragile_or_transitional_resilience"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "resilience_distribution_index":
                round(
                    resilience_distribution_index,
                    4,
                ),
            "resilience_recovery_stability":
                round(
                    resilience_recovery_stability,
                    4,
                ),
            "ecological_recovery_coherence":
                round(
                    ecological_recovery_coherence,
                    4,
                ),
            "resilience_variability":
                round(
                    resilience_variability,
                    4,
                ),
            "collapse_frequency":
                round(
                    collapse_frequency,
                    4,
                ),
            "mean_recovery_latency":
                round(
                    latency_stats["mean"],
                    4,
                ),
            "resilience_class":
                resilience_class,
            "meta_analysis":
                meta_analysis,
        }
