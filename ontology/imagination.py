from __future__ import annotations

PRIMITIVE = "imagination"
DESCRIPTION = "Imagination."
DEPENDENCIES = []

"""
IMAGINATION primitive.

Scientific definition
---------------------
IMAGINATION formalizes the generation of novel possible configurations under
constraints of structural coherence. It quantifies:

- novel_configuration_generation: production of previously unrealized forms.
- structural_coherence: internal consistency of imagined configurations.
- exploratory_diversity: breadth of generated possibilities.
- imagination_index: global synthesis of imaginative capacity.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "IMAGINATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Imagination:
    """Foundational implementation of the IMAGINATION primitive."""

    def __init__(
        self,
        generation_weight: float = 1.0,
        coherence_weight: float = 1.0,
        diversity_weight: float = 1.0,
    ) -> None:
        self.generation_weight = max(0.0, float(generation_weight))
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.diversity_weight = max(0.0, float(diversity_weight))

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
        novel_configurations: Iterable[Any] | None = None,
        coherence_signals: Iterable[Any] | None = None,
        diversity_signals: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        novel_configurations = list(novel_configurations or [])
        coherence_signals = list(coherence_signals or [])
        diversity_signals = list(diversity_signals or [])

        novel_configuration_generation = self._fraction(
            novel_configurations
        )
        structural_coherence = self._fraction(coherence_signals)
        exploratory_diversity = self._fraction(diversity_signals)

        total_weight = (
            self.generation_weight
            + self.coherence_weight
            + self.diversity_weight
        )

        if total_weight <= 0.0:
            imagination_index = 0.0
        else:
            imagination_index = _clamp(
                (
                    self.generation_weight * novel_configuration_generation
                    + self.coherence_weight * structural_coherence
                    + self.diversity_weight * exploratory_diversity
                )
                / total_weight
            )

        status = "nominal" if imagination_index > 0.0 else "empty"

        return {
            "primitive": PRIMITIVE_NAME,
            "novel_configuration_generation": (
                novel_configuration_generation
            ),
            "structural_coherence": structural_coherence,
            "exploratory_diversity": exploratory_diversity,
            "imagination_index": imagination_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "generation_weight": self.generation_weight,
                "coherence_weight": self.coherence_weight,
                "diversity_weight": self.diversity_weight,
                "status": status,
            },
        }

    def step(self, **kwargs: Any) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: Any) -> Dict[str, Any]:
        evaluation = self.evaluate(**kwargs)
        return {
            "primitive": PRIMITIVE_NAME,
            "is_valid": evaluation["imagination_index"] >= 0.0,
            "imagination_index": evaluation["imagination_index"],
            "diagnostics": evaluation["diagnostics"],
        }
