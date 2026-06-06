from __future__ import annotations

PRIMITIVE = "reasoning"
DESCRIPTION = "Reasoning."
DEPENDENCIES = []

"""
REASONING primitive.

Scientific definition
---------------------
REASONING formalizes the structured transformation of concepts into inferred
conclusions. It quantifies:

- inference_coherence: consistency of inferential transitions.
- logical_consistency: absence of contradiction in the reasoning chain.
- conclusion_reliability: robustness of derived conclusions.
- reasoning_index: global synthesis of reasoning quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "REASONING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Reasoning:
    """Foundational implementation of the REASONING primitive."""

    def __init__(
        self,
        inference_weight: float = 1.0,
        consistency_weight: float = 1.0,
        reliability_weight: float = 1.0,
    ) -> None:
        self.inference_weight = max(0.0, float(inference_weight))
        self.consistency_weight = max(0.0, float(consistency_weight))
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
        inferences: Iterable[Any] | None = None,
        consistencies: Iterable[Any] | None = None,
        conclusions: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        inferences = list(inferences or [])
        consistencies = list(consistencies or [])
        conclusions = list(conclusions or [])

        inference_coherence = self._fraction(inferences)
        logical_consistency = self._fraction(consistencies)
        conclusion_reliability = self._fraction(conclusions)

        total_weight = (
            self.inference_weight
            + self.consistency_weight
            + self.reliability_weight
        )

        if total_weight <= 0.0:
            reasoning_index = 0.0
        else:
            reasoning_index = _clamp(
                (
                    self.inference_weight * inference_coherence
                    + self.consistency_weight * logical_consistency
                    + self.reliability_weight * conclusion_reliability
                )
                / total_weight
            )

        status = "nominal" if reasoning_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "inference_coherence": inference_coherence,
            "logical_consistency": logical_consistency,
            "conclusion_reliability": conclusion_reliability,
            "reasoning_index": reasoning_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "inference_weight": self.inference_weight,
                "consistency_weight": self.consistency_weight,
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
            "is_valid": evaluation["reasoning_index"] >= 0.0,
            "reasoning_index": evaluation["reasoning_index"],
            "diagnostics": evaluation["diagnostics"],
        }
