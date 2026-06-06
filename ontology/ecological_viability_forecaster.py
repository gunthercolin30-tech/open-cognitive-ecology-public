
from statistics import mean, pstdev

from ontology.scientific_meta_analysis_engine import (
    ScientificMetaAnalysisEngine
)


class EcologicalViabilityForecaster:

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

    def _projection_slope(self, values):

        if len(values) < 2:
            return 0.0

        return (
            values[-1] - values[0]
        ) / (len(values) - 1)

    def step(self, runs):

        if not runs:
            return {
                "success": False,
                "reason": "no_runs",
            }

        fatigue_values = [
            float(
                r.get(
                    "ecological_fatigue_index",
                    0.0,
                )
            )
            for r in runs
        ]

        acceleration_values = [
            float(
                r.get(
                    "fatigue_acceleration",
                    0.0,
                )
            )
            for r in runs
        ]

        viability_values = [
            float(
                r.get(
                    "ecological_viability",
                    0.0,
                )
            )
            for r in runs
        ]

        degradation_values = [
            float(
                r.get(
                    "irreversible_degradation_risk",
                    0.0,
                )
            )
            for r in runs
        ]

        fatigue_stats = self._safe_stats(
            fatigue_values
        )

        acceleration_stats = self._safe_stats(
            acceleration_values
        )

        viability_stats = self._safe_stats(
            viability_values
        )

        degradation_stats = self._safe_stats(
            degradation_values
        )

        fatigue_projection = (
            self._projection_slope(
                fatigue_values
            )
        )

        viability_projection = (
            self._projection_slope(
                viability_values
            )
        )

        forecasted_viability_index = (
            self._bounded(
                viability_stats["mean"]
                - fatigue_projection
            )
        )

        projected_collapse_risk = (
            self._bounded(
                (
                    fatigue_stats["mean"]
                    + acceleration_stats["mean"]
                    + degradation_stats["mean"]
                ) / 3.0
            )
        )

        viability_horizon_stability = (
            self._bounded(
                forecasted_viability_index
                * (
                    1.0
                    - projected_collapse_risk
                )
            )
        )

        future_resilience_persistence = (
            self._bounded(
                1.0
                - fatigue_stats["mean"]
            )
        )

        studies = []

        for value in viability_values:

            studies.append(
                {
                    "effect_size": value,
                    "variance": max(
                        viability_stats["std_dev"],
                        1e-6,
                    ),
                }
            )

        meta_analysis = (
            self.meta_analysis_engine.step(
                studies
            )
        )

        if viability_horizon_stability >= 0.90:

            forecast_class = (
                "persistent_open_viability"
            )

        elif viability_horizon_stability >= 0.70:

            forecast_class = (
                "adaptive_but_fragile_projection"
            )

        else:

            forecast_class = (
                "fragile_or_collapsing_projection"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "forecasted_viability_index":
                round(
                    forecasted_viability_index,
                    4,
                ),
            "projected_collapse_risk":
                round(
                    projected_collapse_risk,
                    4,
                ),
            "viability_horizon_stability":
                round(
                    viability_horizon_stability,
                    4,
                ),
            "future_resilience_persistence":
                round(
                    future_resilience_persistence,
                    4,
                ),
            "fatigue_projection":
                round(
                    fatigue_projection,
                    4,
                ),
            "viability_projection":
                round(
                    viability_projection,
                    4,
                ),
            "forecast_class":
                forecast_class,
            "meta_analysis":
                meta_analysis,
        }
