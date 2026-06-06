
from statistics import mean, pstdev

from ontology.scientific_meta_analysis_engine import (
    ScientificMetaAnalysisEngine
)


class EcologicalFatigueAnalyzer:

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

    def _fatigue_acceleration(
        self,
        fatigue_values,
    ):

        if len(fatigue_values) < 2:
            return 0.0

        accelerations = []

        for i in range(1, len(fatigue_values)):

            accelerations.append(
                abs(
                    fatigue_values[i]
                    - fatigue_values[i - 1]
                )
            )

        return mean(accelerations)

    def step(self, runs):

        if not runs:
            return {
                "success": False,
                "reason": "no_runs",
            }

        drift_values = [
            float(
                r.get(
                    "recovery_drift",
                    0.0,
                )
            )
            for r in runs
        ]

        stability_values = [
            float(
                r.get(
                    "recovery_stability",
                    0.0,
                )
            )
            for r in runs
        ]

        continuity_values = [
            float(
                r.get(
                    "ecological_recovery_continuity",
                    0.0,
                )
            )
            for r in runs
        ]

        collapse_values = [
            float(
                r.get(
                    "longitudinal_collapse_risk",
                    0.0,
                )
            )
            for r in runs
        ]

        drift_stats = self._safe_stats(
            drift_values
        )

        stability_stats = self._safe_stats(
            stability_values
        )

        continuity_stats = self._safe_stats(
            continuity_values
        )

        collapse_stats = self._safe_stats(
            collapse_values
        )

        ecological_fatigue_index = (
            self._bounded(
                (
                    drift_stats["mean"]
                    + (
                        1.0
                        - stability_stats["mean"]
                    )
                    + (
                        1.0
                        - continuity_stats["mean"]
                    )
                    + collapse_stats["mean"]
                ) / 4.0
            )
        )

        fatigue_acceleration = (
            self._bounded(
                self._fatigue_acceleration(
                    drift_values
                )
            )
        )

        ecological_viability = (
            self._bounded(
                1.0
                - ecological_fatigue_index
            )
        )

        irreversible_degradation_risk = (
            self._bounded(
                (
                    ecological_fatigue_index
                    + fatigue_acceleration
                    + collapse_stats["mean"]
                ) / 3.0
            )
        )

        fatigue_variability = (
            self._bounded(
                drift_stats["std_dev"]
            )
        )

        studies = []

        for value in drift_values:

            studies.append(
                {
                    "effect_size": (
                        1.0 - value
                    ),
                    "variance": max(
                        fatigue_variability,
                        1e-6,
                    ),
                }
            )

        meta_analysis = (
            self.meta_analysis_engine.step(
                studies
            )
        )

        if ecological_fatigue_index < 0.10:

            fatigue_class = (
                "stable_low_fatigue_ecology"
            )

        elif ecological_fatigue_index < 0.30:

            fatigue_class = (
                "moderate_adaptive_fatigue"
            )

        else:

            fatigue_class = (
                "fragile_or_exhausted_ecology"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "ecological_fatigue_index":
                round(
                    ecological_fatigue_index,
                    4,
                ),
            "fatigue_acceleration":
                round(
                    fatigue_acceleration,
                    4,
                ),
            "ecological_viability":
                round(
                    ecological_viability,
                    4,
                ),
            "irreversible_degradation_risk":
                round(
                    irreversible_degradation_risk,
                    4,
                ),
            "fatigue_variability":
                round(
                    fatigue_variability,
                    4,
                ),
            "fatigue_class":
                fatigue_class,
            "meta_analysis":
                meta_analysis,
        }
