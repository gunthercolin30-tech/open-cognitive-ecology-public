from __future__ import annotations

PRIMITIVE = "generalization"
DESCRIPTION = "Generalization."
DEPENDENCIES = []

"""
GENERALIZATION primitive.

Scientific definition
---------------------
GENERALIZATION formalizes the transfer of consolidated structural knowledge
to novel contexts. It quantifies:

- pattern_abstraction: extraction of invariant regularities.
- transfer_effectiveness: success of applying acquired structures elsewhere.
- novel_context_adaptation: adequacy in previously unseen situations.
- generalization_index: global synthesis of generalization quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "GENERALIZATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Generalization:
    """Foundational implementation of the GENERALIZATION primitive."""

    def __init__(
        self,
        abstraction_weight: float = 1.0,
        transfer_weight: float = 1.0,
        adaptation_weight: float = 1.0,
    ) -> None:
        self.abstraction_weight = max(0.0, float(abstraction_weight))
        self.transfer_weight = max(0.0, float(transfer_weight))
        self.adaptation_weight = max(0.0, float(adaptation_weight))

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
        abstractions: Iterable[Any] | None = None,
        transfers: Iterable[Any] | None = None,
        novel_adaptations: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        abstractions = list(abstractions or [])
        transfers = list(transfers or [])
        novel_adaptations = list(novel_adaptations or [])

        pattern_abstraction = self._fraction(abstractions)
        transfer_effectiveness = self._fraction(transfers)
        novel_context_adaptation = self._fraction(novel_adaptations)

        total_weight = (
            self.abstraction_weight
            + self.transfer_weight
            + self.adaptation_weight
        )

        if total_weight <= 0.0:
            generalization_index = 0.0
        else:
            generalization_index = _clamp(
                (
                    self.abstraction_weight * pattern_abstraction
                    + self.transfer_weight * transfer_effectiveness
                    + self.adaptation_weight * novel_context_adaptation
                )
                / total_weight
            )

        status = "nominal" if generalization_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "pattern_abstraction": pattern_abstraction,
            "transfer_effectiveness": transfer_effectiveness,
            "novel_context_adaptation": novel_context_adaptation,
            "generalization_index": generalization_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "abstraction_weight": self.abstraction_weight,
                "transfer_weight": self.transfer_weight,
                "adaptation_weight": self.adaptation_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["generalization_index"] >= 0.0,
            "generalization_index": evaluation["generalization_index"],
            "diagnostics": evaluation["diagnostics"],
        }
