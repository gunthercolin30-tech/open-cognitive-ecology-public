
"""
Intergenerational Continuity Metrics

Lightweight aggregation layer for distributed
intergenerational continuity dynamics.
"""

from statistics import mean


class IntergenerationalContinuityMetrics:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def step(self, runs):

        if not runs:

            return {
                "success": False,
                "reason": "no_runs",
            }

        lineage_integrity = mean([
            float(
                r.get(
                    "lineage_integrity",
                    0.0,
                )
            )
            for r in runs
        ])

        continuity_strength = mean([
            float(
                r.get(
                    "continuity_strength",
                    0.0,
                )
            )
            for r in runs
        ])

        fragmentation_pressure = mean([
            float(
                r.get(
                    "fragmentation_pressure",
                    0.0,
                )
            )
            for r in runs
        ])

        memory_resurgence_rate = mean([
            float(
                r.get(
                    "memory_resurgence_rate",
                    0.0,
                )
            )
            for r in runs
        ])

        collapse_pressure = mean([
            float(
                r.get(
                    "collapse_pressure",
                    0.0,
                )
            )
            for r in runs
        ])

        distributed_openness = mean([
            float(
                r.get(
                    "distributed_openness",
                    0.0,
                )
            )
            for r in runs
        ])

        continuity_index = self._bounded(
            (
                lineage_integrity
                + continuity_strength
                + memory_resurgence_rate
                + distributed_openness
                + (1.0 - fragmentation_pressure)
                + (1.0 - collapse_pressure)
            ) / 6.0
        )

        ecological_stability = self._bounded(
            (
                continuity_strength
                + distributed_openness
                + (1.0 - fragmentation_pressure)
            ) / 3.0
        )

        if continuity_index >= 0.85:

            continuity_class = (
                "stable_open_continuity"
            )

        elif continuity_index >= 0.60:

            continuity_class = (
                "adaptive_fragile_continuity"
            )

        elif continuity_index >= 0.35:

            continuity_class = (
                "fragmented_continuity"
            )

        else:

            continuity_class = (
                "collapsing_lineage_ecology"
            )

        return {
            "success": True,
            "run_count": len(runs),
            "continuity_index":
                round(
                    continuity_index,
                    4,
                ),
            "ecological_stability":
                round(
                    ecological_stability,
                    4,
                ),
            "fragmentation_pressure":
                round(
                    fragmentation_pressure,
                    4,
                ),
            "memory_resurgence_rate":
                round(
                    memory_resurgence_rate,
                    4,
                ),
            "collapse_pressure":
                round(
                    collapse_pressure,
                    4,
                ),
            "distributed_openness":
                round(
                    distributed_openness,
                    4,
                ),
            "continuity_class":
                continuity_class,
        }
