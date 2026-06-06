PRIMITIVE = "coevolutionary_dynamics"
DESCRIPTION = "Coevolutionary dynamics."
DEPENDENCIES = []

"""
COEVOLUTIONARY_DYNAMICS
=======================

Scientific primitive formalizing the reciprocal adaptation of interacting
systems that mutually modify each other's evolutionary trajectories.

The primitive quantifies interaction intensity, mutual adaptation,
coupling strength, and the resulting coevolutionary potential.

Related primitives
------------------
- META_ADAPTATION
- SELECTIVE_PRESSURE
- ADAPTIVE_LANDSCAPE
- OPEN_ENDEDNESS
"""

from typing import Dict, Any


PRIMITIVE_NAME = "COEVOLUTIONARY_DYNAMICS"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class CoevolutionaryDynamics:
    """
    Formal model of reciprocal adaptive change.

    Parameters
    ----------
    interaction_intensity : float
        Strength of interactions between systems.
    mutual_adaptation_rate : float
        Rate of reciprocal adaptive change.
    coupling_strength : float
        Degree of structural coupling.

    Scientific interpretation
    -------------------------
    coevolutionary_potential is the mean of interaction intensity,
    mutual adaptation rate, and coupling strength.
    """

    def __init__(
        self,
        interaction_intensity: float = 0.0,
        mutual_adaptation_rate: float = 0.0,
        coupling_strength: float = 0.0,
    ) -> None:
        self.interaction_intensity = _clamp(interaction_intensity)
        self.mutual_adaptation_rate = _clamp(mutual_adaptation_rate)
        self.coupling_strength = _clamp(coupling_strength)

    def evaluate(self) -> Dict[str, Any]:
        """Compute coevolutionary indicators."""
        coevolutionary_potential = _clamp(
            (
                self.interaction_intensity
                + self.mutual_adaptation_rate
                + self.coupling_strength
            ) / 3.0
        )

        status = (
            "isolated"
            if coevolutionary_potential == 0.0
            else "coevolving"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "interaction_intensity": self.interaction_intensity,
            "mutual_adaptation_rate": self.mutual_adaptation_rate,
            "coupling_strength": self.coupling_strength,
            "status": status,
        }

        return {
            "interaction_intensity": self.interaction_intensity,
            "mutual_adaptation_rate": self.mutual_adaptation_rate,
            "coupling_strength": self.coupling_strength,
            "coevolutionary_potential": coevolutionary_potential,
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
            "interaction_intensity",
            "mutual_adaptation_rate",
            "coupling_strength",
            "coevolutionary_potential",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_coevolving": (
                evaluation["coevolutionary_potential"] > 0.0
            ),
            "coevolutionary_potential": (
                evaluation["coevolutionary_potential"]
            ),
            "diagnostics": evaluation["diagnostics"],
        }
