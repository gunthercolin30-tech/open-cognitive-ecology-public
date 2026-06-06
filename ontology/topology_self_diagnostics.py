from __future__ import annotations

from statistics import mean, pstdev

PRIMITIVE = "topology_self_diagnostics"

DEPENDENCIES = [
    "reflexive_topology_self_revision",
    "topological_pressure_monitor",
    "ontology_topology_governance",
    "implicit_duplication_control",
    "ecological_fatigue_analyzer",
    "resilience_distribution_analyzer",
    "constitutional_longitudinal_observatory",
    "architectural_non_closure_index",
    "distributed_historical_mutation",
    "scientific_meta_analysis_engine",
    "distributed_runtime_coordinator",
]


def _bounded(value: float) -> float:
    return max(
        0.0,
        min(
            1.0,
            float(value),
        ),
    )


class TopologySelfDiagnostics:

    def __init__(
        self,
        instability_threshold: float = 0.70,
        fatigue_threshold: float = 0.55,
    ):
        self.instability_threshold = (
            instability_threshold
        )
        self.fatigue_threshold = (
            fatigue_threshold
        )

        self.history = []

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

        runs = runs or []

        if not runs:

            return {
                "primitive": PRIMITIVE,
                "success": False,
                "reason": "no_runs",
            }

        pressure_values = [
            float(
                r.get(
                    "topological_pressure",
                    0.0,
                )
            )
            for r in runs
        ]

        drift_values = [
            float(
                r.get(
                    "historical_drift",
                    0.0,
                )
            )
            for r in runs
        ]

        openness_values = [
            float(
                r.get(
                    "distributed_openness",
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

        fatigue_values = [
            float(
                r.get(
                    "ecological_fatigue_index",
                    0.0,
                )
            )
            for r in runs
        ]

        non_closure_values = [
            float(
                r.get(
                    "architectural_non_closure_index",
                    0.0,
                )
            )
            for r in runs
        ]

        pressure_stats = self._safe_stats(
            pressure_values
        )

        drift_stats = self._safe_stats(
            drift_values
        )

        openness_stats = self._safe_stats(
            openness_values
        )

        resilience_stats = self._safe_stats(
            resilience_values
        )

        fatigue_stats = self._safe_stats(
            fatigue_values
        )

        non_closure_stats = self._safe_stats(
            non_closure_values
        )

        topological_instability_index = (
            _bounded(
                (
                    pressure_stats["mean"]
                    + drift_stats["mean"]
                    + fatigue_stats["mean"]
                    + (
                        1.0
                        - openness_stats["mean"]
                    )
                ) / 4.0
            )
        )

        distributed_resilience_index = (
            _bounded(
                (
                    resilience_stats["mean"]
                    + non_closure_stats["mean"]
                    + openness_stats["mean"]
                ) / 3.0
            )
        )

        historical_reconvergence_index = (
            _bounded(
                (
                    drift_stats["mean"]
                    + pressure_stats["mean"]
                    + (
                        1.0
                        - non_closure_stats["mean"]
                    )
                ) / 3.0
            )
        )

        fatigue_acceleration = (
            fatigue_stats["std_dev"]
        )

        longitudinal_openness_viability = (
            _bounded(
                (
                    distributed_resilience_index
                    + (
                        1.0
                        - topological_instability_index
                    )
                ) / 2.0
            )
        )

        diagnostics_state = {
            "topological_instability_index":
                round(
                    topological_instability_index,
                    4,
                ),
            "distributed_resilience_index":
                round(
                    distributed_resilience_index,
                    4,
                ),
            "historical_reconvergence_index":
                round(
                    historical_reconvergence_index,
                    4,
                ),
            "fatigue_acceleration":
                round(
                    fatigue_acceleration,
                    4,
                ),
            "longitudinal_openness_viability":
                round(
                    longitudinal_openness_viability,
                    4,
                ),
        }

        self.history.append(
            diagnostics_state
        )

        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        structural_anomaly_detected = (
            topological_instability_index
            >= self.instability_threshold
        )

        ecological_exhaustion_detected = (
            fatigue_stats["mean"]
            >= self.fatigue_threshold
        )

        future_openness_preserved = (
            longitudinal_openness_viability
            >= 0.70
        )

        return {
            "primitive": PRIMITIVE,
            "success": True,
            "diagnostics_active": True,
            "history_size":
                len(self.history),
            "topological_instability_index":
                round(
                    topological_instability_index,
                    4,
                ),
            "distributed_resilience_index":
                round(
                    distributed_resilience_index,
                    4,
                ),
            "historical_reconvergence_index":
                round(
                    historical_reconvergence_index,
                    4,
                ),
            "fatigue_acceleration":
                round(
                    fatigue_acceleration,
                    4,
                ),
            "longitudinal_openness_viability":
                round(
                    longitudinal_openness_viability,
                    4,
                ),
            "structural_anomaly_detected":
                structural_anomaly_detected,
            "ecological_exhaustion_detected":
                ecological_exhaustion_detected,
            "future_openness_preserved":
                future_openness_preserved,
        }
