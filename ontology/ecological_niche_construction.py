PRIMITIVE = "ecological_niche_construction"
DESCRIPTION = "Ecological niche construction."
DEPENDENCIES = []

"""
ECOLOGICAL_NICHE_CONSTRUCTION
============================

Scientific primitive formalizing the active modification of environmental
conditions by systems, thereby altering their own selective and viability
constraints.

The primitive quantifies environmental modification, feedback strength,
niche stability, and the resulting construction potential.

Related primitives
------------------
- COEVOLUTIONARY_DYNAMICS
- CONSTRAINT_FIELDS
- SELECTIVE_PRESSURE
- VIABILITY_DOMAIN
"""

from typing import Dict, Any


PRIMITIVE_NAME = "ECOLOGICAL_NICHE_CONSTRUCTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class EcologicalNicheConstruction:
    """
    Formal model of niche construction.

    Parameters
    ----------
    environment_modification : float
        Degree to which the system alters its environment.
    feedback_strength : float
        Strength of reciprocal environmental feedback.
    niche_stability : float
        Stability of the constructed niche over time.

    Scientific interpretation
    -------------------------
    construction_potential is the mean of environmental modification,
    feedback strength, and niche stability.
    """

    def __init__(
        self,
        environment_modification: float = 0.0,
        feedback_strength: float = 0.0,
        niche_stability: float = 0.0,
    ) -> None:
        self.environment_modification = _clamp(environment_modification)
        self.feedback_strength = _clamp(feedback_strength)
        self.niche_stability = _clamp(niche_stability)

    def evaluate(self) -> Dict[str, Any]:
        """Compute niche construction indicators."""
        construction_potential = _clamp(
            (
                self.environment_modification
                + self.feedback_strength
                + self.niche_stability
            ) / 3.0
        )

        status = (
            "passive"
            if construction_potential == 0.0
            else "constructive"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "environment_modification": self.environment_modification,
            "feedback_strength": self.feedback_strength,
            "niche_stability": self.niche_stability,
            "status": status,
        }

        return {
            "environment_modification": self.environment_modification,
            "feedback_strength": self.feedback_strength,
            "niche_stability": self.niche_stability,
            "construction_potential": construction_potential,
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
            "environment_modification",
            "feedback_strength",
            "niche_stability",
            "construction_potential",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_constructive": (
                evaluation["construction_potential"] > 0.0
            ),
            "construction_potential": (
                evaluation["construction_potential"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
