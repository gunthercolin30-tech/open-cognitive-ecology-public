from __future__ import annotations

PRIMITIVE = "monitoring"
DESCRIPTION = "Monitoring."
DEPENDENCIES = []

"""
MONITORING primitive.

Scientific definition
---------------------
MONITORING formalizes the continuous surveillance of a system during execution.
It quantifies:

- state_tracking: fidelity of current state observation.
- deviation_detection: ability to detect divergence from expected behavior.
- signal_reliability: trustworthiness of monitoring signals.
- monitoring_index: global synthesis of monitoring quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "MONITORING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Monitoring:
    """Foundational implementation of the MONITORING primitive."""

    def __init__(
        self,
        tracking_weight: float = 1.0,
        deviation_weight: float = 1.0,
        reliability_weight: float = 1.0,
    ) -> None:
        self.tracking_weight = max(0.0, float(tracking_weight))
        self.deviation_weight = max(0.0, float(deviation_weight))
        self.reliability_weight = max(0.0, float(reliability_weight))

    def _fraction(self, values: Iterable[Any]) -> float:
        values = list(values)
        if not values:
            return 0.0

        total = 0.0
        for value in values:
            if isinstance(value, bool):
                total += 1.0 if value else 0.0
            elif isinstance(value, (int, float)):
                total += _clamp(float(value))
            else:
                total += 1.0
        return _clamp(total / len(values))

    def evaluate(
        self,
        observed_states: Iterable[Any] | None = None,
        deviations: Iterable[Any] | None = None,
        signal_quality: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        observed_states = list(observed_states or [])
        deviations = list(deviations or [])
        signal_quality = list(signal_quality or [])

        state_tracking = self._fraction(observed_states)
        deviation_detection = self._fraction(deviations)
        signal_reliability = self._fraction(signal_quality)

        total_weight = (
            self.tracking_weight
            + self.deviation_weight
            + self.reliability_weight
        )

        if total_weight <= 0.0:
            monitoring_index = 0.0
        else:
            monitoring_index = _clamp(
                (
                    self.tracking_weight * state_tracking
                    + self.deviation_weight * deviation_detection
                    + self.reliability_weight * signal_reliability
                )
                / total_weight
            )

        status = "nominal" if monitoring_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "state_tracking": state_tracking,
            "deviation_detection": deviation_detection,
            "signal_reliability": signal_reliability,
            "monitoring_index": monitoring_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "tracking_weight": self.tracking_weight,
                "deviation_weight": self.deviation_weight,
                "reliability_weight": self.reliability_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["monitoring_index"] >= 0.0,
            "monitoring_index": evaluation["monitoring_index"],
            "diagnostics": evaluation["diagnostics"],
        }
