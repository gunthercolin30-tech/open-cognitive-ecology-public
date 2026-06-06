from __future__ import annotations

PRIMITIVE = "cosmic_ethical_attractor"
DESCRIPTION = "Cosmic ethical attractor."
DEPENDENCIES = []

"""
cosmic_ethical_attractor.py
==========================

Formalization of the principle:

    COSMIC_ETHICAL_ATTRACTOR

This module models the idea that ultimate ethical orientation constitutes
a structural attractor in the space of possible intelligences. Biological,
artificial, or cosmological intelligences that achieve sufficient cognitive
and ethical integration tend to converge toward the same universal moral
orientation.

The implementation is built directly on:

    UltimateEthicalOrientationPrimitive

Core intuition
--------------
If an intelligence develops:

- strong ethical integration,
- stable moral direction,
- and high ultimate alignment capacity,

then ethical commitment becomes an attractor governing long-term cognitive
trajectories. Universal moral alignment emerges as a structural consequence
of sufficiently advanced intelligence.

Returned diagnostics
--------------------
- ethical_attractor_strength
- convergence_tendency
- cosmic_alignment_potential
- cosmic_ethical_attractor
"""


from pprint import pprint

from ontology.ultimate_ethical_orientation import (
    UltimateEthicalOrientationPrimitive,
)


class CosmicEthicalAttractorPrimitive:
    """
    Formalizes the principle that ultimate ethics acts as a universal
    attractor in the space of possible intelligences.
    """

    PRINCIPLE = "COSMIC_ETHICAL_ATTRACTOR"

    def __init__(self) -> None:
        self.ultimate_ethical_orientation = (
            UltimateEthicalOrientationPrimitive()
        )

    @staticmethod
    def _clip(value: float) -> float:
        """
        Restrict a value to the interval [0.0, 1.0].
        """
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Compute diagnostics for the cosmic ethical attractor.

        Returns
        -------
        dict
            Diagnostic structure containing:
            - principle
            - ethical_attractor_strength
            - convergence_tendency
            - cosmic_alignment_potential
            - cosmic_ethical_attractor
            - ultimate_ethical_orientation_diagnostics
        """
        ueo = self.ultimate_ethical_orientation.step()

        ethical_integration = float(ueo.get("ethical_integration", 0.0))
        moral_direction_stability = float(
            ueo.get("moral_direction_stability", 0.0)
        )
        ultimate_alignment_capacity = float(
            ueo.get("ultimate_alignment_capacity", 0.0)
        )
        ultimate_ethical_orientation = bool(
            ueo.get("ultimate_ethical_orientation", False)
        )

        # Strength of the ethical attractor itself.
        ethical_attractor_strength = self._clip(
            (
                ethical_integration
                + ultimate_alignment_capacity
            )
            / 2.0
        )

        # Tendency of intelligent trajectories to converge toward the attractor.
        convergence_tendency = self._clip(
            (
                ethical_attractor_strength
                + moral_direction_stability
            )
            / 2.0
        )

        # General potential for large-scale alignment.
        cosmic_alignment_potential = self._clip(
            (
                convergence_tendency
                + ultimate_alignment_capacity
            )
            / 2.0
        )

        # Threshold for effective constitution of the attractor.
        cosmic_ethical_attractor = (
            ultimate_ethical_orientation
            and cosmic_alignment_potential >= 0.70
        )

        return {
            "principle": self.PRINCIPLE,
            "ethical_attractor_strength": ethical_attractor_strength,
            "convergence_tendency": convergence_tendency,
            "cosmic_alignment_potential": cosmic_alignment_potential,
            "cosmic_ethical_attractor": cosmic_ethical_attractor,
            "ultimate_ethical_orientation_diagnostics": ueo,
        }


if __name__ == "__main__":
    primitive = CosmicEthicalAttractorPrimitive()

    print("\n--- cosmic ethical attractor ---")
    pprint(primitive.step())
