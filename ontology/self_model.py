from __future__ import annotations

PRIMITIVE = "self_model"
DESCRIPTION = "Self model."
DEPENDENCIES = []

"""
SELF_MODEL primitive.

Scientific definition
---------------------
SELF_MODEL formalizes the internal representation that a system maintains of
its own capacities, limitations, and internal state organization. It quantifies:

- self_representation_coherence: internal consistency of self-description.
- capability_awareness: awareness of available competencies and resources.
- limitation_awareness: awareness of constraints and boundaries.
- self_model_index: global synthesis of self-model quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "SELF_MODEL"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class SelfModel:
    """Foundational implementation of the SELF_MODEL primitive."""

    def __init__(
        self,
        coherence_weight: float = 1.0,
        capability_weight: float = 1.0,
        limitation_weight: float = 1.0,
    ) -> None:
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.capability_weight = max(0.0, float(capability_weight))
        self.limitation_weight = max(0.0, float(limitation_weight))

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
        representation_signals: Iterable[Any] | None = None,
        capability_signals: Iterable[Any] | None = None,
        limitation_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        representation_signals = list(representation_signals or [])
        capability_signals = list(capability_signals or [])
        limitation_signals = list(limitation_signals or [])

        self_representation_coherence = self._fraction(
            representation_signals
        )
        capability_awareness = self._fraction(capability_signals)
        limitation_awareness = self._fraction(limitation_signals)

        total_weight = (
            self.coherence_weight
            + self.capability_weight
            + self.limitation_weight
        )

        if total_weight <= 0.0:
            self_model_index = 0.0
        else:
            self_model_index = _clamp(
                (
                    self.coherence_weight * self_representation_coherence
                    + self.capability_weight * capability_awareness
                    + self.limitation_weight * limitation_awareness
                )
                / total_weight
            )

        status = "nominal" if self_model_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "self_representation_coherence": (
                self_representation_coherence
            ),
            "capability_awareness": capability_awareness,
            "limitation_awareness": limitation_awareness,
            "self_model_index": self_model_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "coherence_weight": self.coherence_weight,
                "capability_weight": self.capability_weight,
                "limitation_weight": self.limitation_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["self_model_index"] >= 0.0,
            "self_model_index": evaluation["self_model_index"],
            "diagnostics": evaluation["diagnostics"],
        }
