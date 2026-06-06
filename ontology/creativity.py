from __future__ import annotations

PRIMITIVE = "creativity"
DESCRIPTION = "Creativity."
DEPENDENCIES = []

"""
CREATIVITY primitive.

Scientific definition
---------------------
CREATIVITY formalizes the production of original configurations that combine
novelty, usefulness, and structural originality. It quantifies:

- novelty: degree of departure from prior configurations.
- usefulness: operational or structural value of generated outputs.
- structural_originality: non-trivial reorganization of constraints.
- creativity_index: global synthesis of creative capacity.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "CREATIVITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Creativity:
    """Foundational implementation of the CREATIVITY primitive."""

    def __init__(
        self,
        novelty_weight: float = 1.0,
        usefulness_weight: float = 1.0,
        originality_weight: float = 1.0,
    ) -> None:
        self.novelty_weight = max(0.0, float(novelty_weight))
        self.usefulness_weight = max(0.0, float(usefulness_weight))
        self.originality_weight = max(0.0, float(originality_weight))

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
        novelty_signals: Iterable[Any] | None = None,
        usefulness_signals: Iterable[Any] | None = None,
        originality_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        novelty_signals = list(novelty_signals or [])
        usefulness_signals = list(usefulness_signals or [])
        originality_signals = list(originality_signals or [])

        novelty = self._fraction(novelty_signals)
        usefulness = self._fraction(usefulness_signals)
        structural_originality = self._fraction(originality_signals)

        total_weight = (
            self.novelty_weight
            + self.usefulness_weight
            + self.originality_weight
        )

        if total_weight <= 0.0:
            creativity_index = 0.0
        else:
            creativity_index = _clamp(
                (
                    self.novelty_weight * novelty
                    + self.usefulness_weight * usefulness
                    + self.originality_weight * structural_originality
                )
                / total_weight
            )

        status = "nominal" if creativity_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "novelty": novelty,
            "usefulness": usefulness,
            "structural_originality": structural_originality,
            "creativity_index": creativity_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "novelty_weight": self.novelty_weight,
                "usefulness_weight": self.usefulness_weight,
                "originality_weight": self.originality_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["creativity_index"] >= 0.0,
            "creativity_index": evaluation["creativity_index"],
            "diagnostics": evaluation["diagnostics"],
        }
