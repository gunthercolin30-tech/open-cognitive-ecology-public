PRIMITIVE = "strategy_selection"
DESCRIPTION = "Strategy selection."
DEPENDENCIES = []

"""
ontology/strategy_selection.py

Scientific primitive: STRATEGY_SELECTION

STRATEGY_SELECTION formalizes the capacity of a system to select a coherent
organization of actions for achieving goals under constraints.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "STRATEGY_SELECTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class StrategySelection:
    """Foundational primitive formalizing coherent strategy choice."""

    def __init__(
        self,
        coherence_weight: float = 1.0,
        alignment_weight: float = 1.0,
        commitment_weight: float = 1.0,
    ) -> None:
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.alignment_weight = max(0.0, float(alignment_weight))
        self.commitment_weight = max(0.0, float(commitment_weight))

    def evaluate(
        self,
        prioritization: float = 0.0,
        decision_making: float = 0.0,
        goal_directedness: float = 0.0,
        controllability: float = 0.0,
    ) -> Dict[str, Any]:
        pr = _clamp(prioritization)
        dm = _clamp(decision_making)
        gd = _clamp(goal_directedness)
        ct = _clamp(controllability)

        plan_coherence = _clamp((pr + gd) / 2.0)
        resource_alignment = _clamp((pr + ct) / 2.0)
        strategy_commitment = _clamp((dm + gd + ct) / 3.0)

        total_weight = (
            self.coherence_weight
            + self.alignment_weight
            + self.commitment_weight
        )

        if total_weight <= 0.0:
            strategy_selection_index = 0.0
        else:
            strategy_selection_index = _clamp(
                (
                    self.coherence_weight * plan_coherence
                    + self.alignment_weight * resource_alignment
                    + self.commitment_weight * strategy_commitment
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "prioritization": pr,
            "decision_making": dm,
            "goal_directedness": gd,
            "controllability": ct,
            "plan_coherence": plan_coherence,
            "resource_alignment": resource_alignment,
            "strategy_commitment": strategy_commitment,
            "status": "computed",
        }

        return {
            "plan_coherence": plan_coherence,
            "resource_alignment": resource_alignment,
            "strategy_commitment": strategy_commitment,
            "strategy_selection_index": strategy_selection_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """Single-step update."""
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """Validate whether strategy selection is non-zero."""
        result = self.evaluate(**kwargs)
        valid = result["strategy_selection_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "strategy_selection_index": result["strategy_selection_index"],
            "diagnostics": diagnostics,
        }
