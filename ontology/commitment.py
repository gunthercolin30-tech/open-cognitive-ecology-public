PRIMITIVE = "commitment"
DESCRIPTION = "Commitment."
DEPENDENCIES = []

"""
ontology/commitment.py

Scientific primitive: COMMITMENT

COMMITMENT formalizes the capacity of a system to maintain a selected
orientation over time despite perturbations and competing alternatives.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "COMMITMENT"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Commitment:
    """Foundational primitive formalizing stabilized engagement."""

    def __init__(
        self,
        lock_in_weight: float = 1.0,
        persistence_weight: float = 1.0,
        reversal_weight: float = 1.0,
    ) -> None:
        self.lock_in_weight = max(0.0, float(lock_in_weight))
        self.persistence_weight = max(0.0, float(persistence_weight))
        self.reversal_weight = max(0.0, float(reversal_weight))

    def evaluate(
        self,
        choice: float = 0.0,
        volition: float = 0.0,
        goal_directedness: float = 0.0,
        structural_continuity: float = 0.0,
    ) -> Dict[str, Any]:
        ch = _clamp(choice)
        vo = _clamp(volition)
        gd = _clamp(goal_directedness)
        sc = _clamp(structural_continuity)

        decision_lock_in = _clamp((ch + vo) / 2.0)
        trajectory_persistence = _clamp((gd + sc) / 2.0)
        resistance_to_reversal = _clamp((ch + vo + sc) / 3.0)

        total_weight = (
            self.lock_in_weight
            + self.persistence_weight
            + self.reversal_weight
        )

        if total_weight <= 0.0:
            commitment_index = 0.0
        else:
            commitment_index = _clamp(
                (
                    self.lock_in_weight * decision_lock_in
                    + self.persistence_weight * trajectory_persistence
                    + self.reversal_weight * resistance_to_reversal
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "choice": ch,
            "volition": vo,
            "goal_directedness": gd,
            "structural_continuity": sc,
            "decision_lock_in": decision_lock_in,
            "trajectory_persistence": trajectory_persistence,
            "resistance_to_reversal": resistance_to_reversal,
            "status": "computed",
        }

        return {
            "decision_lock_in": decision_lock_in,
            "trajectory_persistence": trajectory_persistence,
            "resistance_to_reversal": resistance_to_reversal,
            "commitment_index": commitment_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """Single-step update."""
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """Validate whether commitment is non-zero."""
        result = self.evaluate(**kwargs)
        valid = result["commitment_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "commitment_index": result["commitment_index"],
            "diagnostics": diagnostics,
        }
