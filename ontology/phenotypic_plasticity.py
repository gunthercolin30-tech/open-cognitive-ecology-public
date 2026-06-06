PRIMITIVE = "phenotypic_plasticity"
DESCRIPTION = "Phenotypic plasticity."
DEPENDENCIES = []

"""
PHENOTYPIC_PLASTICITY
=====================

Scientific primitive formalizing the capacity of a single structural
organization to express different functional responses depending on
environmental conditions.

The primitive quantifies environmental sensitivity, response flexibility,
reconfiguration capacity, and resulting plasticity strength.

Related primitives
------------------
- CANALIZATION
- META_ADAPTATION
- VIABILITY_DOMAIN
- ECOLOGICAL_NICHE_CONSTRUCTION
"""

from typing import Dict, Any


PRIMITIVE_NAME = "PHENOTYPIC_PLASTICITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class PhenotypicPlasticity:
    """
    Formal model of context-dependent reconfiguration.

    Parameters
    ----------
    environmental_sensitivity : float
        Degree to which environmental variation is detected.
    response_flexibility : float
        Diversity of possible responses.
    reconfiguration_capacity : float
        Ability to reorganize internal structure.

    Scientific interpretation
    -------------------------
    plasticity_strength is the mean of environmental sensitivity,
    response flexibility, and reconfiguration capacity.
    """

    def __init__(
        self,
        environmental_sensitivity: float = 0.0,
        response_flexibility: float = 0.0,
        reconfiguration_capacity: float = 0.0,
    ) -> None:
        self.environmental_sensitivity = _clamp(
            environmental_sensitivity
        )
        self.response_flexibility = _clamp(response_flexibility)
        self.reconfiguration_capacity = _clamp(
            reconfiguration_capacity
        )

    def evaluate(self) -> Dict[str, Any]:
        """Compute phenotypic plasticity indicators."""
        plasticity_strength = _clamp(
            (
                self.environmental_sensitivity
                + self.response_flexibility
                + self.reconfiguration_capacity
            ) / 3.0
        )

        status = (
            "rigid"
            if plasticity_strength == 0.0
            else "plastic"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "environmental_sensitivity": (
                self.environmental_sensitivity
            ),
            "response_flexibility": self.response_flexibility,
            "reconfiguration_capacity": (
                self.reconfiguration_capacity
            ),
            "status": status,
        }

        return {
            "environmental_sensitivity": (
                self.environmental_sensitivity
            ),
            "response_flexibility": self.response_flexibility,
            "reconfiguration_capacity": (
                self.reconfiguration_capacity
            ),
            "plasticity_strength": plasticity_strength,
            "diagnostics": diagnostics,
        }

    def step(self) -> Dict[str, Any]:
        """Return one evaluation step."""
        return self.evaluate()

    def validate(self) -> Dict[str, Any]:
        """Validate internal coherence."""
        evaluation = self.evaluate()

        valid = True
        for key in (
            "environmental_sensitivity",
            "response_flexibility",
            "reconfiguration_capacity",
            "plasticity_strength",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_plastic": (
                evaluation["plasticity_strength"] > 0.0
            ),
            "plasticity_strength": (
                evaluation["plasticity_strength"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
