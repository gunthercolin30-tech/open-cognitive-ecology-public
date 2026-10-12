from __future__ import annotations

from numbers import Real
from statistics import mean
from typing import Any, Iterable, Mapping

PRIMITIVE = "longitudinal_drift_detection"


class LongitudinalDriftDetection:
    """Detect longitudinal drift from a bounded numeric history.

    The public ``step(values)`` contract is preserved.  Validation and runtime
    callers may additionally provide a mapping containing one of the canonical
    history keys.  Non-numeric metadata is ignored rather than coerced.
    """

    HISTORY_KEYS = (
        "values",
        "history",
        "series",
        "measurements",
        "scores",
        "metrics",
    )

    @staticmethod
    def _is_numeric(value: Any) -> bool:
        return isinstance(value, Real) and not isinstance(value, bool)

    def _extract_numeric_values(self, payload: Any) -> list[float]:
        if payload is None:
            return []

        if self._is_numeric(payload):
            return [float(payload)]

        if isinstance(payload, Mapping):
            for key in self.HISTORY_KEYS:
                if key in payload:
                    extracted = self._extract_numeric_values(payload[key])
                    if extracted:
                        return extracted

            # Generic mappings are accepted only through their numeric values;
            # textual keys such as ``primitive`` are never coerced.
            values: list[float] = []
            for value in payload.values():
                if self._is_numeric(value):
                    values.append(float(value))
                elif isinstance(value, (list, tuple)):
                    values.extend(self._extract_numeric_values(value))
            return values

        if isinstance(payload, (list, tuple)):
            values = []
            for value in payload:
                if self._is_numeric(value):
                    values.append(float(value))
            return values

        return []

    @staticmethod
    def _bounded(value: Any) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(self, values: Any = None, persist: bool = False) -> dict[str, Any]:
        del persist  # This analytical primitive has no persistence side effect.
        numeric_values = self._extract_numeric_values(values)

        if len(numeric_values) < 2:
            return {
                "primitive": PRIMITIVE,
                "success": False,
                "reason": "insufficient_history",
                "sample_count": len(numeric_values),
            }

        drift_rate = abs(numeric_values[-1] - numeric_values[-2])
        cumulative_drift = abs(numeric_values[-1] - numeric_values[0])
        relative_drift = cumulative_drift / max(abs(numeric_values[0]), 1e-9)
        drift_direction = (
            "decreasing"
            if numeric_values[-1] < numeric_values[0]
            else "increasing"
        )

        deltas = [
            numeric_values[index + 1] - numeric_values[index]
            for index in range(len(numeric_values) - 1)
        ]
        drift_acceleration = (
            abs(deltas[-1] - deltas[-2])
            if len(deltas) >= 2
            else 0.0
        )
        critical_drop_detection = relative_drift >= 0.25
        civilizational_drift_index = self._bounded(
            mean(
                [
                    drift_rate,
                    cumulative_drift,
                    relative_drift,
                    drift_acceleration,
                ]
            )
        )

        if critical_drop_detection:
            classification = "critical_longitudinal_drift"
        elif civilizational_drift_index < 0.10:
            classification = "stable_longitudinal_trajectory"
        elif civilizational_drift_index < 0.30:
            classification = "controlled_longitudinal_drift"
        else:
            classification = "critical_longitudinal_drift"

        return {
            "primitive": PRIMITIVE,
            "success": True,
            "sample_count": len(numeric_values),
            "drift_rate": round(drift_rate, 4),
            "drift_acceleration": round(drift_acceleration, 4),
            "cumulative_drift": round(cumulative_drift, 4),
            "relative_drift": round(relative_drift, 4),
            "critical_drop_detection": critical_drop_detection,
            "drift_direction": drift_direction,
            "civilizational_drift_index": round(
                civilizational_drift_index,
                4,
            ),
            "classification": classification,
        }
