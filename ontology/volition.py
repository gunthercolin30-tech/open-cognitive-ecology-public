PRIMITIVE = "volition"
DESCRIPTION = "Volition."
DEPENDENCIES = []

"""
ontology/volition.py

Scientific primitive: VOLITION

VOLITION formalizes the capacity of a system to transform internal motivations
into committed and executable decisions.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "VOLITION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Volition:
    """Foundational primitive formalizing operational decision commitment."""

    def __init__(
        self,
        intent_weight: float = 1.0,
        commitment_weight: float = 1.0,
        execution_weight: float = 1.0,
    ) -> None:
        self.intent_weight = max(0.0, float(intent_weight))
        self.commitment_weight = max(0.0, float(commitment_weight))
        self.execution_weight = max(0.0, float(execution_weight))

    def evaluate(
        self,
        self_determination: float = 0.0,
        autonomy: float = 0.0,
        agency: float = 0.0,
        goal_directedness: float = 0.0,
    ) -> Dict[str, Any]:
        sd = _clamp(self_determination)
        au = _clamp(autonomy)
        ag = _clamp(agency)
        gd = _clamp(goal_directedness)

        intent_strength = _clamp((sd + gd) / 2.0)
        choice_commitment = _clamp((sd + au) / 2.0)
        decision_execution = _clamp((ag + au + gd) / 3.0)

        total_weight = (
            self.intent_weight +
            self.commitment_weight +
            self.execution_weight
        )

        if total_weight <= 0.0:
            volition_index = 0.0
        else:
            volition_index = _clamp(
                (
                    self.intent_weight * intent_strength +
                    self.commitment_weight * choice_commitment +
                    self.execution_weight * decision_execution
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "self_determination": sd,
            "autonomy": au,
            "agency": ag,
            "goal_directedness": gd,
            "intent_strength": intent_strength,
            "choice_commitment": choice_commitment,
            "decision_execution": decision_execution,
            "status": "computed",
        }

        return {
            "intent_strength": intent_strength,
            "choice_commitment": choice_commitment,
            "decision_execution": decision_execution,
            "volition_index": volition_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        result = self.evaluate(**kwargs)
        valid = result["volition_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "volition_index": result["volition_index"],
            "diagnostics": diagnostics,
        }
