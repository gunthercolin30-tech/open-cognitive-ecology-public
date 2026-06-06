PRIMITIVE = "choice"
DESCRIPTION = "Choice."
DEPENDENCIES = []

"""
ontology/choice.py

Scientific primitive: CHOICE

CHOICE formalizes the elementary act through which one alternative among
multiple possibilities becomes operationally actualized.
"""

from typing import Dict, Any

PRIMITIVE_NAME = "CHOICE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Choice:
    """Foundational primitive formalizing branch selection."""

    def __init__(
        self,
        resolution_weight: float = 1.0,
        commitment_weight: float = 1.0,
        actualization_weight: float = 1.0,
    ) -> None:
        self.resolution_weight = max(0.0, float(resolution_weight))
        self.commitment_weight = max(0.0, float(commitment_weight))
        self.actualization_weight = max(0.0, float(actualization_weight))

    def evaluate(
        self,
        decision_making: float = 0.0,
        volition: float = 0.0,
        intentionality: float = 0.0,
        reachability: float = 0.0,
    ) -> Dict[str, Any]:
        dm = _clamp(decision_making)
        vo = _clamp(volition)
        it = _clamp(intentionality)
        re = _clamp(reachability)

        alternative_resolution = _clamp((dm + it) / 2.0)
        selection_commitment = _clamp((vo + dm) / 2.0)
        branch_actualization = _clamp((re + vo + it) / 3.0)

        total_weight = (
            self.resolution_weight
            + self.commitment_weight
            + self.actualization_weight
        )

        if total_weight <= 0.0:
            choice_index = 0.0
        else:
            choice_index = _clamp(
                (
                    self.resolution_weight * alternative_resolution
                    + self.commitment_weight * selection_commitment
                    + self.actualization_weight * branch_actualization
                ) / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "decision_making": dm,
            "volition": vo,
            "intentionality": it,
            "reachability": re,
            "alternative_resolution": alternative_resolution,
            "selection_commitment": selection_commitment,
            "branch_actualization": branch_actualization,
            "status": "computed",
        }

        return {
            "alternative_resolution": alternative_resolution,
            "selection_commitment": selection_commitment,
            "branch_actualization": branch_actualization,
            "choice_index": choice_index,
            "diagnostics": diagnostics,
        }

    def step(self, **kwargs: float) -> Dict[str, Any]:
        return self.evaluate(**kwargs)

    def validate(self, **kwargs: float) -> Dict[str, Any]:
        result = self.evaluate(**kwargs)
        valid = result["choice_index"] > 0.0

        diagnostics = dict(result["diagnostics"])
        diagnostics["status"] = "valid" if valid else "invalid"

        return {
            "valid": valid,
            "choice_index": result["choice_index"],
            "diagnostics": diagnostics,
        }
