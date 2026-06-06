PRIMITIVE = "evaluation"
DESCRIPTION = "Evaluation."
DEPENDENCIES = []

"""
ontology/evaluation.py

Scientific primitive: EVALUATION

EVALUATION formalizes the application of internal value structures to
alternatives or states in order to generate an operational judgment.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "EVALUATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Evaluation:
    """Foundational primitive formalizing operational judgment."""

    def __init__(
        self,
        criterion_weight: float = 1.0,
        assessment_weight: float = 1.0,
        consistency_weight: float = 1.0,
    ) -> None:
        self.criterion_weight = max(0.0, float(criterion_weight))
        self.assessment_weight = max(0.0, float(assessment_weight))
        self.consistency_weight = max(0.0, float(consistency_weight))

    def evaluate(
        self,
        value_formation: float = 0.0,
        preference: float = 0.0,
        decision_making: float = 0.0,
        intentionality: float = 0.0,
    ) -> Dict[str, Any]:
        vf = _clamp(value_formation)
        pr = _clamp(preference)
        dm = _clamp(decision_making)
        it = _clamp(intentionality)

        criterion_application = _clamp((vf + it) / 2.0)
        outcome_assessment = _clamp((pr + dm) / 2.0)
        judgment_consistency = _clamp((vf + pr + it) / 3.0)

        total_weight = (
            self.criterion_weight
            + self.assessment_weight
            + self.consistency_weight
        )

        if total_weight <= 0.0:
            evaluation_index = 0.0
        else:
            evaluation_index = _clamp(
                (
                    self.criterion_weight * criterion_application
                    + self.assessment_weight * outcome_assessment
                    + self.consistency_weight * judgment_consistency
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "value_formation": vf,
            "preference": pr,
            "decision_making": dm,
            "intentionality": it,
            "criterion_application": criterion_application,
            "outcome_assessment": outcome_assessment,
            "judgment_consistency": judgment_consistency,
            "status": "computed",
        }

        return {
            "criterion_application": criterion_application,
            "outcome_assessment": outcome_assessment,
            "judgment_consistency": judgment_consistency,
            "evaluation_index": evaluation_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """Single-step update."""
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """Validate whether evaluation is non-zero."""
        result = self.evaluate(**kwargs)
        valid = result["evaluation_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "evaluation_index": result["evaluation_index"],
            "diagnostics": diagnostics,
        }
