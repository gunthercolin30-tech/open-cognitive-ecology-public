PRIMITIVE = "novelty_emergence"
DESCRIPTION = "Novelty emergence."
DEPENDENCIES = []

"""
NOVELTY_EMERGENCE
=================

Scientific primitive formalizing the local appearance of genuinely new
configurations under recombination, surprise, and irreducible uncertainty.

The primitive quantifies the probability and intensity of emergence of
previously non-instantiated structures.

Related primitives
------------------
- OPEN_ENDEDNESS
- NON_REPRESENTABILITY
- QUANTUM_INDETERMINACY
- EVOLUTIONARY_DRIFT
"""

from typing import Dict, Any


PRIMITIVE_NAME = "NOVELTY_EMERGENCE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    """Clamp a numerical value to the interval [0, 1]."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class NoveltyEmergence:
    """
    Formal model of novelty generation.

    Parameters
    ----------
    recombination_potential : float
        Capacity to combine existing structures in new ways.
    surprise_factor : float
        Degree of unpredictability associated with outcomes.
    openness_support : float
        Background support for sustained novelty production.

    Scientific interpretation
    -------------------------
    novelty_probability is the mean of recombination and surprise.
    emergence_intensity combines novelty probability and openness support.
    """

    def __init__(
        self,
        recombination_potential: float = 0.0,
        surprise_factor: float = 0.0,
        openness_support: float = 0.0,
    ) -> None:
        self.recombination_potential = _clamp(recombination_potential)
        self.surprise_factor = _clamp(surprise_factor)
        self.openness_support = _clamp(openness_support)

    def evaluate(self) -> Dict[str, Any]:
        """Compute novelty emergence indicators."""
        novelty_probability = _clamp(
            (self.recombination_potential + self.surprise_factor) / 2.0
        )
        emergence_intensity = _clamp(
            (novelty_probability + self.openness_support) / 2.0
        )

        status = (
            "static"
            if emergence_intensity == 0.0
            else "emergent"
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "recombination_potential": self.recombination_potential,
            "surprise_factor": self.surprise_factor,
            "openness_support": self.openness_support,
            "status": status,
        }

        return {
            "recombination_potential": self.recombination_potential,
            "surprise_factor": self.surprise_factor,
            "novelty_probability": novelty_probability,
            "emergence_intensity": emergence_intensity,
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
            "recombination_potential",
            "surprise_factor",
            "novelty_probability",
            "emergence_intensity",
        ):
            if not (0.0 <= evaluation[key] <= 1.0):
                valid = False
                break

        return {
            "valid": valid,
            "is_emergent": evaluation["emergence_intensity"] > 0.0,
            "emergence_intensity": evaluation["emergence_intensity"],
            "diagnostics": evaluation["diagnostics"],
        }
