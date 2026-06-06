from __future__ import annotations

PRIMITIVE = "insight"
DESCRIPTION = "Insight."
DEPENDENCIES = []

"""
INSIGHT primitive.

Scientific definition
---------------------
INSIGHT formalizes abrupt cognitive restructuring that yields a more compact
and effective understanding of a problem or situation. It quantifies:

- restructuring_intensity: magnitude of structural reorganization.
- solution_compactness: reduction in explanatory or operational complexity.
- understanding_gain: increase in coherent understanding.
- insight_index: global synthesis of insight quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "INSIGHT"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Insight:
    """Foundational implementation of the INSIGHT primitive."""

    def __init__(
        self,
        restructuring_weight: float = 1.0,
        compactness_weight: float = 1.0,
        understanding_weight: float = 1.0,
    ) -> None:
        self.restructuring_weight = max(0.0, float(restructuring_weight))
        self.compactness_weight = max(0.0, float(compactness_weight))
        self.understanding_weight = max(0.0, float(understanding_weight))

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
        restructuring_signals: Iterable[Any] | None = None,
        compactness_signals: Iterable[Any] | None = None,
        understanding_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        restructuring_signals = list(restructuring_signals or [])
        compactness_signals = list(compactness_signals or [])
        understanding_signals = list(understanding_signals or [])

        restructuring_intensity = self._fraction(
            restructuring_signals
        )
        solution_compactness = self._fraction(compactness_signals)
        understanding_gain = self._fraction(understanding_signals)

        total_weight = (
            self.restructuring_weight
            + self.compactness_weight
            + self.understanding_weight
        )

        if total_weight <= 0.0:
            insight_index = 0.0
        else:
            insight_index = _clamp(
                (
                    self.restructuring_weight * restructuring_intensity
                    + self.compactness_weight * solution_compactness
                    + self.understanding_weight * understanding_gain
                )
                / total_weight
            )

        status = "nominal" if insight_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "restructuring_intensity": restructuring_intensity,
            "solution_compactness": solution_compactness,
            "understanding_gain": understanding_gain,
            "insight_index": insight_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "restructuring_weight": self.restructuring_weight,
                "compactness_weight": self.compactness_weight,
                "understanding_weight": self.understanding_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["insight_index"] >= 0.0,
            "insight_index": evaluation["insight_index"],
            "diagnostics": evaluation["diagnostics"],
        }
