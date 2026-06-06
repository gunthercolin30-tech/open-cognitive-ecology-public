from __future__ import annotations

PRIMITIVE = "conscious_access"
DESCRIPTION = "Conscious access."
DEPENDENCIES = []

"""
CONSCIOUS_ACCESS primitive.

Scientific definition
---------------------
CONSCIOUS_ACCESS formalizes the global availability of information to multiple
cognitive processes. It quantifies:

- global_availability: extent to which relevant information is broadly accessible.
- broadcast_coherence: consistency of information dissemination.
- access_stability: persistence of information availability over time.
- conscious_access_index: global synthesis of conscious accessibility.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "CONSCIOUS_ACCESS"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class ConsciousAccess:
    """Foundational implementation of the CONSCIOUS_ACCESS primitive."""

    def __init__(
        self,
        availability_weight: float = 1.0,
        coherence_weight: float = 1.0,
        stability_weight: float = 1.0,
    ) -> None:
        self.availability_weight = max(0.0, float(availability_weight))
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.stability_weight = max(0.0, float(stability_weight))

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
        availability_signals: Iterable[Any] | None = None,
        coherence_signals: Iterable[Any] | None = None,
        stability_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        availability_signals = list(availability_signals or [])
        coherence_signals = list(coherence_signals or [])
        stability_signals = list(stability_signals or [])

        global_availability = self._fraction(availability_signals)
        broadcast_coherence = self._fraction(coherence_signals)
        access_stability = self._fraction(stability_signals)

        total_weight = (
            self.availability_weight
            + self.coherence_weight
            + self.stability_weight
        )

        if total_weight <= 0.0:
            conscious_access_index = 0.0
        else:
            conscious_access_index = _clamp(
                (
                    self.availability_weight * global_availability
                    + self.coherence_weight * broadcast_coherence
                    + self.stability_weight * access_stability
                )
                / total_weight
            )

        status = "nominal" if conscious_access_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "global_availability": global_availability,
            "broadcast_coherence": broadcast_coherence,
            "access_stability": access_stability,
            "conscious_access_index": conscious_access_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "availability_weight": self.availability_weight,
                "coherence_weight": self.coherence_weight,
                "stability_weight": self.stability_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["conscious_access_index"] >= 0.0,
            "conscious_access_index": evaluation["conscious_access_index"],
            "diagnostics": evaluation["diagnostics"],
        }
