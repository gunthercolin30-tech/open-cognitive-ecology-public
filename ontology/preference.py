PRIMITIVE = "preference"
DESCRIPTION = "Preference."
DEPENDENCIES = []

"""
ontology/preference.py

Scientific primitive: PREFERENCE

PREFERENCE formalizes the relative ordering through which a system
discriminates some alternatives as more desirable than others.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "PREFERENCE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Preference:
    """Foundational primitive formalizing comparative valuation."""

    def __init__(
        self,
        valuation_weight: float = 1.0,
        stability_weight: float = 1.0,
        bias_weight: float = 1.0,
    ) -> None:
        self.valuation_weight = max(0.0, float(valuation_weight))
        self.stability_weight = max(0.0, float(stability_weight))
        self.bias_weight = max(0.0, float(bias_weight))

    def evaluate(
        self,
        decision_making: float = 0.0,
        choice: float = 0.0,
        intentionality: float = 0.0,
        goal_directedness: float = 0.0,
    ) -> Dict[str, Any]:
        dm = _clamp(decision_making)
        ch = _clamp(choice)
        it = _clamp(intentionality)
        gd = _clamp(goal_directedness)

        comparative_valuation = _clamp((dm + it) / 2.0)
        ranking_stability = _clamp((ch + dm) / 2.0)
        selection_bias = _clamp((gd + ch + it) / 3.0)

        total_weight = (
            self.valuation_weight
            + self.stability_weight
            + self.bias_weight
        )

        if total_weight <= 0.0:
            preference_index = 0.0
        else:
            preference_index = _clamp(
                (
                    self.valuation_weight * comparative_valuation
                    + self.stability_weight * ranking_stability
                    + self.bias_weight * selection_bias
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "decision_making": dm,
            "choice": ch,
            "intentionality": it,
            "goal_directedness": gd,
            "comparative_valuation": comparative_valuation,
            "ranking_stability": ranking_stability,
            "selection_bias": selection_bias,
            "status": "computed",
        }

        return {
            "comparative_valuation": comparative_valuation,
            "ranking_stability": ranking_stability,
            "selection_bias": selection_bias,
            "preference_index": preference_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """Single-step update."""
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """Validate whether preference is non-zero."""
        result = self.evaluate(**kwargs)
        valid = result["preference_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "preference_index": result["preference_index"],
            "diagnostics": diagnostics,
        }
