from __future__ import annotations

PRIMITIVE = "error_correction"
DESCRIPTION = "Error correction."
DEPENDENCIES = []

"""
ERROR_CORRECTION primitive.

Scientific definition
---------------------
ERROR_CORRECTION formalizes the identification and compensation of deviations
between observed and target states. It quantifies:

- error_identification: ability to detect and characterize errors.
- correction_effectiveness: efficacy of corrective interventions.
- residual_error_reduction: proportion of remaining error eliminated.
- error_correction_index: global synthesis of correction quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "ERROR_CORRECTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class ErrorCorrection:
    """Foundational implementation of the ERROR_CORRECTION primitive."""

    def __init__(
        self,
        identification_weight: float = 1.0,
        effectiveness_weight: float = 1.0,
        reduction_weight: float = 1.0,
    ) -> None:
        self.identification_weight = max(0.0, float(identification_weight))
        self.effectiveness_weight = max(0.0, float(effectiveness_weight))
        self.reduction_weight = max(0.0, float(reduction_weight))

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
        detected_errors: Iterable[Any] | None = None,
        corrective_actions: Iterable[Any] | None = None,
        residual_reductions: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        detected_errors = list(detected_errors or [])
        corrective_actions = list(corrective_actions or [])
        residual_reductions = list(residual_reductions or [])

        error_identification = self._fraction(detected_errors)
        correction_effectiveness = self._fraction(corrective_actions)
        residual_error_reduction = self._fraction(residual_reductions)

        total_weight = (
            self.identification_weight
            + self.effectiveness_weight
            + self.reduction_weight
        )

        if total_weight <= 0.0:
            error_correction_index = 0.0
        else:
            error_correction_index = _clamp(
                (
                    self.identification_weight * error_identification
                    + self.effectiveness_weight * correction_effectiveness
                    + self.reduction_weight * residual_error_reduction
                )
                / total_weight
            )

        status = "nominal" if error_correction_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "error_identification": error_identification,
            "correction_effectiveness": correction_effectiveness,
            "residual_error_reduction": residual_error_reduction,
            "error_correction_index": error_correction_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "identification_weight": self.identification_weight,
                "effectiveness_weight": self.effectiveness_weight,
                "reduction_weight": self.reduction_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["error_correction_index"] >= 0.0,
            "error_correction_index": evaluation["error_correction_index"],
            "diagnostics": evaluation["diagnostics"],
        }
