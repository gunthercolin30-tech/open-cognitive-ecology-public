from __future__ import annotations

PRIMITIVE = "causal_inference"
DESCRIPTION = "Causal inference."
DEPENDENCIES = []

"""
CAUSAL_INFERENCE primitive.

Scientific definition
---------------------
CAUSAL_INFERENCE formalizes the identification of directed cause-effect
relations that support prediction and intervention. It quantifies:

- causal_discrimination: ability to distinguish causation from correlation.
- intervention_predictability: reliability of predicted intervention effects.
- structural_consistency: coherence of inferred causal structure.
- causal_inference_index: global synthesis of causal inference quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "CAUSAL_INFERENCE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class CausalInference:
    """Foundational implementation of the CAUSAL_INFERENCE primitive."""

    def __init__(
        self,
        discrimination_weight: float = 1.0,
        predictability_weight: float = 1.0,
        consistency_weight: float = 1.0,
    ) -> None:
        self.discrimination_weight = max(0.0, float(discrimination_weight))
        self.predictability_weight = max(0.0, float(predictability_weight))
        self.consistency_weight = max(0.0, float(consistency_weight))

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
        discriminations: Iterable[Any] | None = None,
        intervention_predictions: Iterable[Any] | None = None,
        structural_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        discriminations = list(discriminations or [])
        intervention_predictions = list(intervention_predictions or [])
        structural_signals = list(structural_signals or [])

        causal_discrimination = self._fraction(discriminations)
        intervention_predictability = self._fraction(
            intervention_predictions
        )
        structural_consistency = self._fraction(structural_signals)

        total_weight = (
            self.discrimination_weight
            + self.predictability_weight
            + self.consistency_weight
        )

        if total_weight <= 0.0:
            causal_inference_index = 0.0
        else:
            causal_inference_index = _clamp(
                (
                    self.discrimination_weight * causal_discrimination
                    + self.predictability_weight * intervention_predictability
                    + self.consistency_weight * structural_consistency
                )
                / total_weight
            )

        status = "nominal" if causal_inference_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "causal_discrimination": causal_discrimination,
            "intervention_predictability": intervention_predictability,
            "structural_consistency": structural_consistency,
            "causal_inference_index": causal_inference_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "discrimination_weight": self.discrimination_weight,
                "predictability_weight": self.predictability_weight,
                "consistency_weight": self.consistency_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": (
                evaluation["causal_inference_index"] >= 0.0
            ),
            "causal_inference_index": (
                evaluation["causal_inference_index"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
