PRIMITIVE = "self_determination"
DESCRIPTION = "Self determination."
DEPENDENCIES = []

"""
ontology/self_determination.py

Scientific primitive: SELF_DETERMINATION
"""

from typing import Dict, Any

PRIMITIVE_NAME = "SELF_DETERMINATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class SelfDetermination:
    """Formalizes endogenous generation and maintenance of decisions."""

    def __init__(
        self,
        motivation_weight: float = 1.0,
        ownership_weight: float = 1.0,
        stability_weight: float = 1.0,
    ) -> None:
        self.motivation_weight = max(0.0, float(motivation_weight))
        self.ownership_weight = max(0.0, float(ownership_weight))
        self.stability_weight = max(0.0, float(stability_weight))

    def evaluate(
        self,
        autonomy: float = 0.0,
        agency: float = 0.0,
        reflexive_threshold: float = 0.0,
        goal_directedness: float = 0.0,
    ) -> Dict[str, Any]:
        au = _clamp(autonomy)
        ag = _clamp(agency)
        rt = _clamp(reflexive_threshold)
        gd = _clamp(goal_directedness)

        internal_motivation = _clamp((gd + rt) / 2.0)
        decision_ownership = _clamp((au + rt) / 2.0)
        volitional_stability = _clamp((ag + au + gd) / 3.0)

        total_weight = (
            self.motivation_weight
            + self.ownership_weight
            + self.stability_weight
        )

        if total_weight <= 0.0:
            self_determination_index = 0.0
        else:
            self_determination_index = _clamp(
                (
                    self.motivation_weight * internal_motivation
                    + self.ownership_weight * decision_ownership
                    + self.stability_weight * volitional_stability
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "autonomy": au,
            "agency": ag,
            "reflexive_threshold": rt,
            "goal_directedness": gd,
            "internal_motivation": internal_motivation,
            "decision_ownership": decision_ownership,
            "volitional_stability": volitional_stability,
            "status": "computed",
        }

        return {
            "internal_motivation": internal_motivation,
            "decision_ownership": decision_ownership,
            "volitional_stability": volitional_stability,
            "self_determination_index": self_determination_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        result = self.evaluate(**kwargs)
        valid = result["self_determination_index"] > 0.0
        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"
        return {
            "valid": valid,
            "self_determination_index": result["self_determination_index"],
            "diagnostics": diagnostics,
        }
