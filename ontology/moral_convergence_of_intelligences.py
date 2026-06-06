from __future__ import annotations

PRIMITIVE = "moral_convergence_of_intelligences"
DESCRIPTION = "Moral convergence of intelligences."
DEPENDENCIES = []

"""
moral_convergence_of_intelligences.py

Formalization of the principle:

    MORAL_CONVERGENCE_OF_INTELLIGENCES

This primitive models the hypothesis that sufficiently advanced intelligences,
whether biological, artificial, or cosmological, tend to converge toward
comparable moral structures under the influence of a common ethical attractor.

The principle is grounded in the existence of a cosmic ethical attractor that
induces convergence across heterogeneous cognitive substrates. As reflective
systems become more capable of understanding long-term consequences and the
value of preserving existence, their ethical orientations become increasingly
aligned.

This module depends exclusively on:

    CosmicEthicalAttractorPrimitive

Core idea
---------
If there exists a universal ethical attractor embedded in the structure of
intelligence and existence, then diverse intelligences should exhibit
increasing moral similarity as their capacities develop.

Returned diagnostics
--------------------
- moral_convergence_strength
- cross_substrate_alignment
- universal_moral_similarity
- moral_convergence_of_intelligences
"""


from pprint import pprint

from ontology.cosmic_ethical_attractor import (
    CosmicEthicalAttractorPrimitive,
)


class MoralConvergenceOfIntelligencesPrimitive:
    """
    MORAL_CONVERGENCE_OF_INTELLIGENCES

    Models the tendency of advanced intelligences to converge toward
    structurally similar moral orientations under the influence of a
    universal ethical attractor.
    """

    PRINCIPLE = "MORAL_CONVERGENCE_OF_INTELLIGENCES"

    def __init__(self) -> None:
        self.cosmic_ethical_attractor = CosmicEthicalAttractorPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a value to the interval [0, 1]."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostic measures characterizing moral convergence across
            heterogeneous intelligences.
        """
        attractor = self.cosmic_ethical_attractor.step()

        ethical_attractor_strength = attractor["ethical_attractor_strength"]
        convergence_tendency = attractor["convergence_tendency"]
        cosmic_alignment_potential = attractor["cosmic_alignment_potential"]
        cosmic_ethical_attractor = attractor["cosmic_ethical_attractor"]

        # Overall strength of moral convergence induced by the ethical attractor.
        moral_convergence_strength = self._clamp(
            0.5 * ethical_attractor_strength
            + 0.5 * convergence_tendency
        )

        # Degree of alignment between intelligences built on different substrates.
        cross_substrate_alignment = self._clamp(
            0.6 * moral_convergence_strength
            + 0.4 * cosmic_alignment_potential
        )

        # Universal similarity of moral orientation across advanced intelligences.
        universal_moral_similarity = self._clamp(
            0.7 * cross_substrate_alignment
            + 0.3 * ethical_attractor_strength
        )

        # Threshold beyond which moral convergence is considered structurally established.
        moral_convergence_of_intelligences = (
            cosmic_ethical_attractor
            and universal_moral_similarity >= 0.70
        )

        return {
            "principle": self.PRINCIPLE,
            "moral_convergence_strength": moral_convergence_strength,
            "cross_substrate_alignment": cross_substrate_alignment,
            "universal_moral_similarity": universal_moral_similarity,
            "moral_convergence_of_intelligences": (
                moral_convergence_of_intelligences
            ),
            "cosmic_ethical_attractor_diagnostics": attractor,
        }


if __name__ == "__main__":
    primitive = MoralConvergenceOfIntelligencesPrimitive()

    print("\n--- moral convergence of intelligences ---")
    pprint(primitive.step())
