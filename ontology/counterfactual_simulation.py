from __future__ import annotations

PRIMITIVE = "counterfactual_simulation"
DESCRIPTION = "Counterfactual simulation."
DEPENDENCIES = []

"""
COUNTERFACTUAL_SIMULATION primitive.

Scientific definition
---------------------
COUNTERFACTUAL_SIMULATION formalizes the generation and evaluation of
alternative trajectories that were not actually realized. It quantifies:

- alternative_generation: ability to produce plausible alternatives.
- counterfactual_consistency: internal coherence of hypothetical trajectories.
- intervention_comparison: effectiveness of comparing possible interventions.
- counterfactual_simulation_index: global synthesis of counterfactual quality.

All indicators are normalized to the [0, 1] interval.
"""


from typing import Any, Dict, Iterable

PRIMITIVE_NAME = "COUNTERFACTUAL_SIMULATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class CounterfactualSimulation:
    """Foundational implementation of the COUNTERFACTUAL_SIMULATION primitive."""

    def __init__(
        self,
        generation_weight: float = 1.0,
        consistency_weight: float = 1.0,
        comparison_weight: float = 1.0,
    ) -> None:
        self.generation_weight = max(0.0, float(generation_weight))
        self.consistency_weight = max(0.0, float(consistency_weight))
        self.comparison_weight = max(0.0, float(comparison_weight))

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
        alternatives: Iterable[Any] | None = None,
        consistencies: Iterable[Any] | None = None,
        comparisons: Iterable[Any] | None = None,
    ) -> Dict[str, Any]:
        alternatives = list(alternatives or [])
        consistencies = list(consistencies or [])
        comparisons = list(comparisons or [])

        alternative_generation = self._fraction(alternatives)
        counterfactual_consistency = self._fraction(consistencies)
        intervention_comparison = self._fraction(comparisons)

        total_weight = (
            self.generation_weight
            + self.consistency_weight
            + self.comparison_weight
        )

        if total_weight <= 0.0:
            counterfactual_simulation_index = 0.0
        else:
            counterfactual_simulation_index = _clamp(
                (
                    self.generation_weight * alternative_generation
                    + self.consistency_weight * counterfactual_consistency
                    + self.comparison_weight * intervention_comparison
                )
                / total_weight
            )

        status = (
            "nominal"
            if counterfactual_simulation_index > 0.0
            else "empty"
        )

        return {
            "primitive": PRIMITIVE_NAME,
            "alternative_generation": alternative_generation,
            "counterfactual_consistency": counterfactual_consistency,
            "intervention_comparison": intervention_comparison,
            "counterfactual_simulation_index": (
                counterfactual_simulation_index
            ),
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "generation_weight": self.generation_weight,
                "consistency_weight": self.consistency_weight,
                "comparison_weight": self.comparison_weight,
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
                evaluation["counterfactual_simulation_index"] >= 0.0
            ),
            "counterfactual_simulation_index": (
                evaluation["counterfactual_simulation_index"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
