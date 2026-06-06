PRIMITIVE = "exaptation"
DESCRIPTION = "Exaptation."
DEPENDENCIES = []

"""
EXAPTATION
==========

Scientific primitive formalizing the reuse of an existing structure for a
new function that was not the original target of selection.

The primitive quantifies functional repurposing, latent utility,
cooption probability, and resulting exaptation potential.

Related primitives
------------------
- PHENOTYPIC_PLASTICITY
- NOVELTY_EMERGENCE
- INNOVATION_RETENTION
- SELECTIVE_PRESSURE
"""

from typing import Dict, Any


PRIMITIVE_NAME = "EXAPTATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class Exaptation:
    """
    Formal model of functional co-option.

    Parameters
    ----------
    functional_repurposing : float
        Degree to which an existing structure can be reassigned.
    latent_utility : float
        Presence of previously unused functional potential.
    cooption_probability : float
        Probability that the structure is recruited for a new role.

    Scientific interpretation
    -------------------------
    exaptation_potential is the mean of functional repurposing,
    latent utility, and cooption probability.
    """

    def __init__(
        self,
        functional_repurposing: float = 0.0,
        latent_utility: float = 0.0,
        cooption_probability: float = 0.0,
    ) -> None:
        self.functional_repurposing = _clamp(functional_repurposing)
        self.latent_utility = _clamp(latent_utility)
        self.cooption_probability = _clamp(cooption_probability)

    def evaluate(self) -> Dict[str, Any]:
        """Compute exaptation indicators."""
        exaptation_potential = _clamp(
            (
                self.functional_repurposing
                + self.latent_utility
                + self.cooption_probability
            ) / 3.0
        )

        status = (
            "specialized"
            if exaptation_potential == 0.0
            else "exaptive"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "functional_repurposing": self.functional_repurposing,
            "latent_utility": self.latent_utility,
            "cooption_probability": self.cooption_probability,
            "status": status,
        }

        return {
            "functional_repurposing": self.functional_repurposing,
            "latent_utility": self.latent_utility,
            "cooption_probability": self.cooption_probability,
            "exaptation_potential": exaptation_potential,
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
            "functional_repurposing",
            "latent_utility",
            "cooption_probability",
            "exaptation_potential",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_exaptive": evaluation["exaptation_potential"] > 0.0,
            "exaptation_potential": evaluation["exaptation_potential"],
            "diagnostics": evaluation["diagnostics"],
        }
