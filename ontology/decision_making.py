PRIMITIVE = "decision_making"
DESCRIPTION = "Decision making."
DEPENDENCIES = []

"""
ontology/decision_making.py

Scientific primitive: DECISION_MAKING

DECISION_MAKING formalizes the capacity of a system to evaluate alternatives,
select one option, and maintain commitment to the chosen trajectory.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "DECISION_MAKING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class DecisionMaking:
    """Foundational primitive formalizing selection among alternatives."""

    def __init__(
        self,
        evaluation_weight: float = 1.0,
        confidence_weight: float = 1.0,
        stability_weight: float = 1.0,
    ) -> None:
        self.evaluation_weight = max(0.0, float(evaluation_weight))
        self.confidence_weight = max(0.0, float(confidence_weight))
        self.stability_weight = max(0.0, float(stability_weight))

    def evaluate(
        self,
        intentionality: float = 0.0,
        volition: float = 0.0,
        agency: float = 0.0,
        controllability: float = 0.0,
    ) -> Dict[str, Any]:
        it = _clamp(intentionality)
        vo = _clamp(volition)
        ag = _clamp(agency)
        ct = _clamp(controllability)

        option_evaluation = _clamp((it + ct) / 2.0)
        selection_confidence = _clamp((vo + it) / 2.0)
        commitment_stability = _clamp((ag + vo + ct) / 3.0)

        total_weight = (
            self.evaluation_weight
            + self.confidence_weight
            + self.stability_weight
        )

        if total_weight <= 0.0:
            decision_making_index = 0.0
        else:
            decision_making_index = _clamp(
                (
                    self.evaluation_weight * option_evaluation
                    + self.confidence_weight * selection_confidence
                    + self.stability_weight * commitment_stability
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "intentionality": it,
            "volition": vo,
            "agency": ag,
            "controllability": ct,
            "option_evaluation": option_evaluation,
            "selection_confidence": selection_confidence,
            "commitment_stability": commitment_stability,
            "status": "computed",
        }

        return {
            "option_evaluation": option_evaluation,
            "selection_confidence": selection_confidence,
            "commitment_stability": commitment_stability,
            "decision_making_index": decision_making_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        result = self.evaluate(**kwargs)
        valid = result["decision_making_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "decision_making_index": result["decision_making_index"],
            "diagnostics": diagnostics,
        }
