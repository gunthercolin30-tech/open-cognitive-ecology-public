
from statistics import mean, pstdev

from ontology.scientific_meta_analysis_engine import (
    ScientificMetaAnalysisEngine
)


class LongitudinalRecoveryObserver:

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

    def _compute_recovery_drift(
        self,
        values,
    ):

        if len(values) < 2:
            return 0.0

        return abs(
            values[-1] - values[0]
        )

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

        coherence_values = [
            float(
                r.get(
                    "ecological_recovery_coherence",
                    0.0,
                )
            )
            for r in runs
        ]

        collapse_values = [
            float(
                r.get(
                    "collapse_frequency",
                    0.0,
                )
            )
            for r in runs
        ]

        resilience_stats = self._safe_stats(
            resilience_values
        )

        coherence_stats = self._safe_stats(
            coherence_values
        )

        collapse_stats = self._safe_stats(
            collapse_values
        )

        recovery_drift = (
            self._compute_recovery_drift(
                resilience_values
            )
        )

        longitudinal_recovery_index = (
            self._bounded(
                (
                    resilience_stats["mean"]
                    + coherence_stats["mean"]
                    + (
                        1.0
                        - collapse_stats["mean"]
                    )
                ) / 3.0
            )
        )

        longitudinal_collapse_risk = (
            self._bounded(
                collapse_stats["mean"]
            )
        )

        recovery_stability = (
            self._bounded(
                1.0
                - resilience_stats["std_dev"]
            )
        )

        ecological_recovery_continuity = (
            self._bounded(
                longitudinal_recovery_index
                * recovery_stability
            )
        )

        studies = []

        for value in resilience_values:

            studies.append(
                {
                    "effect_size": value,
                    "variance": max(
                        resilience_stats["std_dev"],
                        1e-6,
                    ),
                }
            )

        meta_analysis = (
            self.meta_analysis_engine.step(
                studies
            )
        )

        if (
            ecological_recovery_continuity >= 0.90
            and recovery_drift < 0.05
        ):

            recovery_class = (
                "persistent_longitudinal_recovery"
            )

        elif ecological_recovery_continuity >= 0.75:

            recovery_class = (
                "functional_longitudinal_recovery"
            )

        else:

            recovery_class = (
                "fragile_or_degrading_recovery"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "longitudinal_recovery_index":
                round(
                    longitudinal_recovery_index,
                    4,
                ),
            "recovery_drift":
                round(
                    recovery_drift,
                    4,
                ),
            "recovery_stability":
                round(
                    recovery_stability,
                    4,
                ),
            "ecological_recovery_continuity":
                round(
                    ecological_recovery_continuity,
                    4,
                ),
            "longitudinal_collapse_risk":
                round(
                    longitudinal_collapse_risk,
                    4,
                ),
            "recovery_class":
                recovery_class,
            "meta_analysis":
                meta_analysis,
        }
