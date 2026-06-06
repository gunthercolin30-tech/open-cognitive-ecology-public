from __future__ import annotations

from statistics import mean

PRIMITIVE = "structural_anomaly_detection"

DEPENDENCIES = [
    "topology_self_diagnostics",
    "reflexive_topology_self_revision",
    "attractor_persistence_analyzer",
    "structural_attractor",
    "trajectory_convergence",
    "trajectory_bifurcation",
    "semantic_collapse",
    "social_ecological_resilience",
    "ecological_fatigue_analyzer",
    "resilience_distribution_analyzer",
    "architectural_non_closure_index",
    "distributed_historical_mutation",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class StructuralAnomalyDetection:

    def __init__(
        self,
        critical_instability_threshold: float = 0.85,
        fragmentation_threshold: float = 0.75,
    ):
        self.critical_instability_threshold = (
            critical_instability_threshold
        )

        self.fragmentation_threshold = (
            fragmentation_threshold
        )

    def step(self, runs):

        runs = runs or []

        if not runs:

            return {
                "primitive": PRIMITIVE,
                "success": False,
                "reason": "no_runs",
            }

        instability_values = [
            float(
                r.get(
                    "topological_instability_index",
                    0.0,
                )
            )
            for r in runs
        ]

        reconvergence_values = [
            float(
                r.get(
                    "historical_reconvergence_index",
                    0.0,
                )
            )
            for r in runs
        ]

        resilience_values = [
            float(
                r.get(
                    "distributed_resilience_index",
                    0.0,
                )
            )
            for r in runs
        ]

        fragmentation_values = [
            float(
                r.get(
                    "semantic_fragmentation",
                    0.0,
                )
            )
            for r in runs
        ]

        basin_values = [
            float(
                r.get(
                    "basin_stability_index",
                    0.0,
                )
            )
            for r in runs
        ]

        socio_values = [
            float(
                r.get(
                    "social_ecological_resilience_index",
                    0.0,
                )
            )
            for r in runs
        ]

        instability_mean = mean(
            instability_values
        )

        reconvergence_mean = mean(
            reconvergence_values
        )

        resilience_mean = mean(
            resilience_values
        )

        fragmentation_mean = mean(
            fragmentation_values
        )

        basin_mean = mean(
            basin_values
        )

        socio_mean = mean(
            socio_values
        )

        fossilization_risk = _bounded(
            (
                instability_mean
                + reconvergence_mean
                + basin_mean
                + fragmentation_mean
                + (
                    1.0 - resilience_mean
                )
            ) / 5.0
        )

        reversibility_index = _bounded(
            (
                resilience_mean
                + socio_mean
                + (
                    1.0 - basin_mean
                )
            ) / 3.0
        )

        anomaly_severity = _bounded(
            (
                fossilization_risk
                + (
                    1.0 - reversibility_index
                )
            ) / 2.0
        )

        if (
            fossilization_risk >= 0.90
            and reversibility_index <= 0.25
        ):
            anomaly_class = (
                "fossilizing_structural_attractor"
            )

        elif (
            fragmentation_mean
            >= self.fragmentation_threshold
        ):
            anomaly_class = (
                "critical_fragmentation"
            )

        elif (
            instability_mean
            >= self.critical_instability_threshold
        ):
            anomaly_class = (
                "critical_topological_instability"
            )

        elif (
            reconvergence_mean >= 0.70
        ):
            anomaly_class = (
                "historical_reconvergence"
            )

        else:
            anomaly_class = (
                "adaptive_or_transitional"
            )

        future_openness_viability = _bounded(
            (
                reversibility_index
                + (
                    1.0 - fossilization_risk
                )
            ) / 2.0
        )

        return {
            "primitive": PRIMITIVE,
            "success": True,
            "anomaly_class":
                anomaly_class,
            "fossilization_risk":
                round(
                    fossilization_risk,
                    4,
                ),
            "reversibility_index":
                round(
                    reversibility_index,
                    4,
                ),
            "anomaly_severity":
                round(
                    anomaly_severity,
                    4,
                ),
            "future_openness_viability":
                round(
                    future_openness_viability,
                    4,
                ),
            "critical_anomaly_detected":
                anomaly_severity >= 0.80,
            "fragmentation_detected":
                fragmentation_mean
                >= self.fragmentation_threshold,
            "historical_reconvergence_detected":
                reconvergence_mean >= 0.70,
            "reversibility_preserved":
                reversibility_index >= 0.45,
        }
