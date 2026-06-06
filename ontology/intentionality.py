PRIMITIVE = "intentionality"
DESCRIPTION = "Intentionality."
DEPENDENCIES = []

"""
ontology/intentionality.py

Scientific primitive: INTENTIONALITY

INTENTIONALITY formalizes the directedness of internal states and actions
toward specific targets, objects, or future configurations.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "INTENTIONALITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Intentionality:
    """Foundational primitive formalizing semantic and operational directedness."""

    def __init__(
        self,
        aboutness_weight: float = 1.0,
        target_weight: float = 1.0,
        orientation_weight: float = 1.0,
    ) -> None:
        self.aboutness_weight = max(0.0, float(aboutness_weight))
        self.target_weight = max(0.0, float(target_weight))
        self.orientation_weight = max(0.0, float(orientation_weight))

    def evaluate(
        self,
        volition: float = 0.0,
        goal_directedness: float = 0.0,
        observability: float = 0.0,
        reflexive_threshold: float = 0.0,
    ) -> Dict[str, Any]:
        vo = _clamp(volition)
        gd = _clamp(goal_directedness)
        ob = _clamp(observability)
        rt = _clamp(reflexive_threshold)

        aboutness = _clamp((vo + gd) / 2.0)
        target_specification = _clamp((gd + ob) / 2.0)
        semantic_orientation = _clamp((vo + rt + gd) / 3.0)

        total_weight = (
            self.aboutness_weight
            + self.target_weight
            + self.orientation_weight
        )

        if total_weight <= 0.0:
            intentionality_index = 0.0
        else:
            intentionality_index = _clamp(
                (
                    self.aboutness_weight * aboutness
                    + self.target_weight * target_specification
                    + self.orientation_weight * semantic_orientation
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "volition": vo,
            "goal_directedness": gd,
            "observability": ob,
            "reflexive_threshold": rt,
            "aboutness": aboutness,
            "target_specification": target_specification,
            "semantic_orientation": semantic_orientation,
            "status": "computed",
        }

        return {
            "aboutness": aboutness,
            "target_specification": target_specification,
            "semantic_orientation": semantic_orientation,
            "intentionality_index": intentionality_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        result = self.evaluate(**kwargs)
        valid = result["intentionality_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "intentionality_index": result["intentionality_index"],
            "diagnostics": diagnostics,
        }
