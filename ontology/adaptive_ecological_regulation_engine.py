
"""
Adaptive Ecological Regulation Engine
"""

from statistics import mean, pstdev


class AdaptiveEcologicalRegulationEngine:

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

    def step(self, runs):

        if not runs:
            return {
                "success": False,
                "reason": "no_runs",
            }

        viability_values = [
            float(
                r.get(
                    "forecasted_viability_index",
                    0.0,
                )
            )
            for r in runs
        ]

        collapse_values = [
            float(
                r.get(
                    "projected_collapse_risk",
                    0.0,
                )
            )
            for r in runs
        ]

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

        stability_values = [
            float(
                r.get(
                    "viability_horizon_stability",
                    0.0,
                )
            )
            for r in runs
        ]

        viability_stats = self._safe_stats(
            viability_values
        )

        collapse_stats = self._safe_stats(
            collapse_values
        )

        fatigue_stats = self._safe_stats(
            fatigue_values
        )

        acceleration_stats = self._safe_stats(
            acceleration_values
        )

        stability_stats = self._safe_stats(
            stability_values
        )

        regulation_pressure = self._bounded(
            (
                collapse_stats["mean"]
                + fatigue_stats["mean"]
                + acceleration_stats["mean"]
            ) / 3.0
        )

        adaptive_openness_score = self._bounded(
            viability_stats["mean"]
            * (
                1.0
                - regulation_pressure
            )
        )

        prospective_stabilization_index = (
            self._bounded(
                (
                    adaptive_openness_score
                    + stability_stats["mean"]
                ) / 2.0
            )
        )

        fatigue_mitigation_factor = (
            self._bounded(
                1.0
                - fatigue_stats["mean"]
            )
        )

        if (
            prospective_stabilization_index >= 0.90
        ):

            regulation_class = (
                "stable_open_regulation"
            )

        elif (
            prospective_stabilization_index >= 0.70
        ):

            regulation_class = (
                "adaptive_low_pressure_regulation"
            )

        else:

            regulation_class = (
                "fragile_or_overcorrective_regulation"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "regulation_pressure":
                round(
                    regulation_pressure,
                    4,
                ),
            "adaptive_openness_score":
                round(
                    adaptive_openness_score,
                    4,
                ),
            "prospective_stabilization_index":
                round(
                    prospective_stabilization_index,
                    4,
                ),
            "fatigue_mitigation_factor":
                round(
                    fatigue_mitigation_factor,
                    4,
                ),
            "regulation_class":
                regulation_class,
        }
