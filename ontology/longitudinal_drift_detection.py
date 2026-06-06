
from statistics import mean

PRIMITIVE = "longitudinal_drift_detection"

class LongitudinalDriftDetection:

    def _bounded(self, value):
        return max(0.0, min(1.0, float(value)))

    def step(self, values):

        values = [float(v) for v in values]

        if len(values) < 2:
            return {
                "success": False,
                "reason": "insufficient_history",
            }

        drift_rate = abs(values[-1] - values[-2])

        cumulative_drift = abs(values[-1] - values[0])

        relative_drift = (
            cumulative_drift / max(values[0], 1e-9)
        )

        drift_direction = (
            "decreasing"
            if values[-1] < values[0]
            else "increasing"
        )

        deltas = [
            values[i + 1] - values[i]
            for i in range(len(values)-1)
        ]

        if len(deltas) >= 2:
            drift_acceleration = abs(
                deltas[-1] - deltas[-2]
            )
        else:
            drift_acceleration = 0.0

        critical_drop_detection = (
            relative_drift >= 0.25
        )

        civilizational_drift_index = self._bounded(
            mean([
                drift_rate,
                cumulative_drift,
                relative_drift,
                drift_acceleration,
            ])
        )

        if critical_drop_detection:
            classification = (
                "critical_longitudinal_drift"
            )
        elif civilizational_drift_index < 0.10:
            classification = (
                "stable_longitudinal_trajectory"
            )
        elif civilizational_drift_index < 0.30:
            classification = (
                "controlled_longitudinal_drift"
            )
        else:
            classification = (
                "critical_longitudinal_drift"
            )

        return {
            "success": True,
            "drift_rate": round(drift_rate, 4),
            "drift_acceleration": round(drift_acceleration, 4),
            "cumulative_drift": round(cumulative_drift, 4),
            "relative_drift": round(relative_drift, 4),
            "critical_drop_detection": critical_drop_detection,
            "drift_direction": drift_direction,
            "civilizational_drift_index":
                round(civilizational_drift_index, 4),
            "classification": classification,
        }
