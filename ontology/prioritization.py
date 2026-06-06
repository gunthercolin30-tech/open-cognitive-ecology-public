PRIMITIVE = "prioritization"
DESCRIPTION = "Prioritization."
DEPENDENCIES = []

"""
ontology/prioritization.py

Scientific primitive: PRIORITIZATION

PRIORITIZATION formalizes the ordering of alternatives, goals, or actions
according to their relative importance and the resulting focus of resources.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "PRIORITIZATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Prioritization:
    """Foundational primitive formalizing ordered allocation of focus."""

    def __init__(
        self,
        ordering_weight: float = 1.0,
        focus_weight: float = 1.0,
        commitment_weight: float = 1.0,
    ) -> None:
        self.ordering_weight = max(0.0, float(ordering_weight))
        self.focus_weight = max(0.0, float(focus_weight))
        self.commitment_weight = max(0.0, float(commitment_weight))

    def evaluate(
        self,
        evaluation: float = 0.0,
        preference: float = 0.0,
        decision_making: float = 0.0,
        commitment: float = 0.0,
    ) -> Dict[str, Any]:
        ev = _clamp(evaluation)
        pr = _clamp(preference)
        dm = _clamp(decision_making)
        cm = _clamp(commitment)

        importance_ordering = _clamp((ev + pr) / 2.0)
        resource_focus = _clamp((ev + dm) / 2.0)
        ranking_commitment = _clamp((pr + dm + cm) / 3.0)

        total_weight = (
            self.ordering_weight
            + self.focus_weight
            + self.commitment_weight
        )

        if total_weight <= 0.0:
            prioritization_index = 0.0
        else:
            prioritization_index = _clamp(
                (
                    self.ordering_weight * importance_ordering
                    + self.focus_weight * resource_focus
                    + self.commitment_weight * ranking_commitment
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "evaluation": ev,
            "preference": pr,
            "decision_making": dm,
            "commitment": cm,
            "importance_ordering": importance_ordering,
            "resource_focus": resource_focus,
            "ranking_commitment": ranking_commitment,
            "status": "computed",
        }

        return {
            "importance_ordering": importance_ordering,
            "resource_focus": resource_focus,
            "ranking_commitment": ranking_commitment,
            "prioritization_index": prioritization_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """Single-step update."""
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """Validate whether prioritization is non-zero."""
        result = self.evaluate(**kwargs)
        valid = result["prioritization_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "prioritization_index": result["prioritization_index"],
            "diagnostics": diagnostics,
        }
