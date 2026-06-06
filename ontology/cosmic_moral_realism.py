from __future__ import annotations

PRIMITIVE = "cosmic_moral_realism"
DESCRIPTION = "Cosmic moral realism."
DEPENDENCIES = []

"""
ontology/cosmic_moral_realism.py

Formalization of the principle COSMIC_MORAL_REALISM.

This module implements the idea that moral structures are not merely local
conventions or contingent preferences, but objective invariants of the space of
possible intelligences. Under this view, ethics is embedded in the structural
organization of cognition and reality itself.

The primitive builds directly upon ObjectiveEthicsUnderConstraintsPrimitive,
which establishes that normativity can emerge from the invariant constraints
governing viable intelligence.

Principle
---------
COSMIC_MORAL_REALISM

Interpretation
--------------
If objective ethics emerges from the structure of constraints, and if these
ethical structures remain invariant across substrates and contexts, then
normativity is part of the deep architecture of the cognitive cosmos.

Diagnostics
-----------
moral_reality_strength
    Degree to which moral structures possess objective reality.

ethical_invariance
    Degree to which ethical structures remain stable across contexts and
    implementations.

cosmic_normative_structure
    Degree to which normativity is integrated into the structure of reality.

cosmic_moral_realism
    Whether objective moral realism is effectively constituted.
"""


from pprint import pprint

from ontology.objective_ethics_under_constraints import (
    ObjectiveEthicsUnderConstraintsPrimitive,
)


class CosmicMoralRealismPrimitive:
    """
    Primitive formalizing COSMIC_MORAL_REALISM.

    Moral realism is treated here as a structural consequence of objective ethics
    grounded in invariant constraints. Ethics becomes a real feature of the
    cognitive cosmos rather than an arbitrary cultural artifact.
    """

    PRINCIPLE = "COSMIC_MORAL_REALISM"

    def __init__(self) -> None:
        self.objective_ethics = ObjectiveEthicsUnderConstraintsPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a value to the [0.0, 1.0] interval."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics describing the emergence of cosmic moral realism.
        """
        upstream = self.objective_ethics.step()

        ethical_objectivity_strength = self._clamp(
            upstream.get("ethical_objectivity_strength", 0.0)
        )
        constraint_grounded_normativity = self._clamp(
            upstream.get("constraint_grounded_normativity", 0.0)
        )
        universality_of_ethics = self._clamp(
            upstream.get("universality_of_ethics", 0.0)
        )
        objective_ethics_under_constraints = bool(
            upstream.get("objective_ethics_under_constraints", False)
        )

        # Degree to which moral structures possess objective reality.
        moral_reality_strength = self._clamp(
            (
                ethical_objectivity_strength
                + constraint_grounded_normativity
            )
            / 2.0
        )

        # Stability of ethical structures across substrates and contexts.
        ethical_invariance = self._clamp(
            (
                moral_reality_strength
                + universality_of_ethics
            )
            / 2.0
        )

        # Integration of normativity into the architecture of reality.
        cosmic_normative_structure = self._clamp(
            (
                ethical_invariance
                + constraint_grounded_normativity
            )
            / 2.0
        )

        # Minimal structural threshold for constituting moral realism.
        threshold = 0.60

        cosmic_moral_realism = (
            objective_ethics_under_constraints
            and cosmic_normative_structure >= threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "moral_reality_strength": moral_reality_strength,
            "ethical_invariance": ethical_invariance,
            "cosmic_normative_structure": cosmic_normative_structure,
            "cosmic_moral_realism": cosmic_moral_realism,
            "objective_ethics_under_constraints_diagnostics": upstream,
        }


if __name__ == "__main__":
    primitive = CosmicMoralRealismPrimitive()

    print("\n--- cosmic moral realism ---")
    pprint(primitive.step())
