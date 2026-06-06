PRIMITIVE = "value_formation"
DESCRIPTION = "Value formation."
DEPENDENCIES = []

"""
ontology/value_formation.py

Scientific primitive: VALUE_FORMATION

VALUE_FORMATION formalizes the emergence and stabilization of internal
criteria used by a system to assign relative importance to states, actions,
and outcomes.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "VALUE_FORMATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numeric value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class ValueFormation:
    """Foundational primitive formalizing endogenous value generation."""

    def __init__(
        self,
        importance_weight: float = 1.0,
        stability_weight: float = 1.0,
        coherence_weight: float = 1.0,
    ) -> None:
        self.importance_weight = max(0.0, float(importance_weight))
        self.stability_weight = max(0.0, float(stability_weight))
        self.coherence_weight = max(0.0, float(coherence_weight))

    def evaluate(
        self,
        preference: float = 0.0,
        intentionality: float = 0.0,
        self_determination: float = 0.0,
        autonomy: float = 0.0,
    ) -> Dict[str, Any]:
        pr = _clamp(preference)
        it = _clamp(intentionality)
        sd = _clamp(self_determination)
        au = _clamp(autonomy)

        importance_assignment = _clamp((pr + it) / 2.0)
        criterion_stability = _clamp((sd + au) / 2.0)
        valuation_coherence = _clamp((pr + sd + au) / 3.0)

        total_weight = (
            self.importance_weight
            + self.stability_weight
            + self.coherence_weight
        )

        if total_weight <= 0.0:
            value_formation_index = 0.0
        else:
            value_formation_index = _clamp(
                (
                    self.importance_weight * importance_assignment
                    + self.stability_weight * criterion_stability
                    + self.coherence_weight * valuation_coherence
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "preference": pr,
            "intentionality": it,
            "self_determination": sd,
            "autonomy": au,
            "importance_assignment": importance_assignment,
            "criterion_stability": criterion_stability,
            "valuation_coherence": valuation_coherence,
            "status": "computed",
        }

        return {
            "importance_assignment": importance_assignment,
            "criterion_stability": criterion_stability,
            "valuation_coherence": valuation_coherence,
            "value_formation_index": value_formation_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        """Single-step update."""
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        """Validate whether value formation is non-zero."""
        result = self.evaluate(**kwargs)
        valid = result["value_formation_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "value_formation_index": result["value_formation_index"],
            "diagnostics": diagnostics,
        }
