
from __future__ import annotations

from statistics import mean
from datetime import datetime

PRIMITIVE = "topological_pressure_monitor"

DEPENDENCIES = [
    "ontology_topology_governance",
    "monitoring",
    "long_duration_runtime_supervisor",
    "alerting_and_notification_system",
    "architectural_non_closure_index",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class TopologicalPressureMonitor:

    def __init__(self):
        self.primitive = PRIMITIVE
        self.history = []

    def _compute_gradient(
        self,
        current,
        previous,
    ):
        return round(
            current - previous,
            6,
        )

    def step(
        self,
        pressure_signal: float = 0.15,
        density_signal: float = 0.20,
        rigidity_signal: float = 0.10,
    ):

        pressure_signal = _bounded(
            pressure_signal
        )

        density_signal = _bounded(
            density_signal
        )

        rigidity_signal = _bounded(
            rigidity_signal
        )

        topological_pressure = _bounded(
            (
                pressure_signal
                + density_signal
                + rigidity_signal
            ) / 3.0
        )

        closure_acceleration = 0.0

        if self.history:

            previous = self.history[-1]

            closure_acceleration = (
                self._compute_gradient(
                    topological_pressure,
                    previous[
                        "topological_pressure"
                    ],
                )
            )

        attractor_rigidity = _bounded(
            (
                rigidity_signal
                + topological_pressure
            ) / 2.0
        )

        convergence_risk = _bounded(
            (
                attractor_rigidity
                + density_signal
            ) / 2.0
        )

        singularity_risk = _bounded(
            (
                convergence_risk
                + abs(
                    closure_acceleration
                )
            ) / 2.0
        )

        topological_openness = _bounded(
            1.0
            - topological_pressure
        )

        anomaly_detected = (
            topological_pressure >= 0.70
            or singularity_risk >= 0.70
        )

        historical_drift = (
            mean(
                [
                    x[
                        "topological_pressure"
                    ]
                    for x in self.history
                ]
            )
            if self.history
            else topological_pressure
        )

        state = {
            "timestamp":
                datetime.utcnow()
                .isoformat() + "Z",
            "topological_pressure":
                topological_pressure,
        }

        self.history.append(state)

        if len(self.history) > 500:
            self.history = self.history[-500:]

        future_openness_preserved = (
            topological_openness >= 0.70
        )

        return {
            "primitive": PRIMITIVE,
            "monitoring_active": True,
            "topological_pressure":
                round(
                    topological_pressure,
                    4,
                ),
            "closure_acceleration":
                round(
                    closure_acceleration,
                    6,
                ),
            "attractor_rigidity":
                round(
                    attractor_rigidity,
                    4,
                ),
            "convergence_risk":
                round(
                    convergence_risk,
                    4,
                ),
            "singularity_risk":
                round(
                    singularity_risk,
                    4,
                ),
            "historical_drift":
                round(
                    historical_drift,
                    4,
                ),
            "topological_openness":
                round(
                    topological_openness,
                    4,
                ),
            "anomaly_detected":
                anomaly_detected,
            "future_openness_preserved":
                future_openness_preserved,
            "history_size":
                len(
                    self.history
                ),
        }


if __name__ == "__main__":

    engine = TopologicalPressureMonitor()

    print(
        engine.step()
    )
