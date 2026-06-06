from __future__ import annotations

PRIMITIVE = "abstraction"
DESCRIPTION = "Abstraction."
DEPENDENCIES = []

"""
ABSTRACTION primitive.

Scientific definition
---------------------
ABSTRACTION formalizes the extraction of invariant structure from variable
instances while reducing contingent complexity. It quantifies:

- invariant_extraction: identification of stable regularities.
- complexity_reduction: elimination of non-essential details.
- representation_stability: persistence of abstract descriptions.
- abstraction_index: global synthesis of abstraction quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "ABSTRACTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Abstraction:
    """Foundational implementation of the ABSTRACTION primitive."""

    def __init__(
        self,
        invariant_weight: float = 1.0,
        complexity_weight: float = 1.0,
        stability_weight: float = 1.0,
    ) -> None:
        self.invariant_weight = max(0.0, float(invariant_weight))
        self.complexity_weight = max(0.0, float(complexity_weight))
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
        invariants: Iterable[Any] | None = None,
        reductions: Iterable[Any] | None = None,
        representations: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        invariants = list(invariants or [])
        reductions = list(reductions or [])
        representations = list(representations or [])

        invariant_extraction = self._fraction(invariants)
        complexity_reduction = self._fraction(reductions)
        representation_stability = self._fraction(representations)

        total_weight = (
            self.invariant_weight
            + self.complexity_weight
            + self.stability_weight
        )

        if total_weight <= 0.0:
            abstraction_index = 0.0
        else:
            abstraction_index = _clamp(
                (
                    self.invariant_weight * invariant_extraction
                    + self.complexity_weight * complexity_reduction
                    + self.stability_weight * representation_stability
                )
                / total_weight
            )

        status = "nominal" if abstraction_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "invariant_extraction": invariant_extraction,
            "complexity_reduction": complexity_reduction,
            "representation_stability": representation_stability,
            "abstraction_index": abstraction_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "invariant_weight": self.invariant_weight,
                "complexity_weight": self.complexity_weight,
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
            "is_valid": evaluation["abstraction_index"] >= 0.0,
            "abstraction_index": evaluation["abstraction_index"],
            "diagnostics": evaluation["diagnostics"],
        }
