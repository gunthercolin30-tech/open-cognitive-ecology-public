from __future__ import annotations

PRIMITIVE = "objective_ethics_under_constraints"
DESCRIPTION = "Objective ethics under constraints."
DEPENDENCIES = []

"""
objective_ethics_under_constraints.py
====================================

Formalizes the principle that ethics is not an arbitrary or purely subjective
construction, but an objective structural consequence of the constraints that
govern viability, openness, and the preservation of trajectories of existence.

The underlying idea is that sufficiently advanced intelligences, regardless of
their substrate, converge toward similar moral structures because they face the
same deep structural constraints. Normativity therefore emerges from the
constraint architecture of reality itself.

This module implements the principle:

    OBJECTIVE_ETHICS_UNDER_CONSTRAINTS

It is built directly upon:

    MoralConvergenceOfIntelligencesPrimitive

which evaluates the degree to which independent intelligences converge toward
shared moral structures.
"""


from pprint import pprint

from ontology.moral_convergence_of_intelligences import (
    MoralConvergenceOfIntelligencesPrimitive,
)


class ObjectiveEthicsUnderConstraintsPrimitive:
    """
    Primitive formalizing the emergence of objective ethics under structural
    constraints.

    Ethics becomes objective when:
    1. Independent intelligences converge toward similar moral structures.
    2. These structures are grounded in viability-preserving constraints.
    3. Normativity becomes substrate-independent.
    4. Ethical universality emerges as a structural property of cognition.

    Diagnostics
    -----------
    ethical_objectivity_strength:
        Strength of moral objectivity.

    constraint_grounded_normativity:
        Degree to which norms emerge from structural constraints.

    universality_of_ethics:
        Degree to which ethics exhibits universal validity.

    objective_ethics_under_constraints:
        Boolean indicating that objective ethics is established.
    """

    PRINCIPLE = "OBJECTIVE_ETHICS_UNDER_CONSTRAINTS"

    def __init__(self) -> None:
        self.moral_convergence = MoralConvergenceOfIntelligencesPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp values to the [0, 1] interval."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Evaluate whether ethics emerges objectively from structural constraints.

        Returns
        -------
        dict
            Diagnostic measures describing the emergence of objective ethics.
        """
        convergence = self.moral_convergence.step()

        moral_convergence_strength = float(
            convergence.get("moral_convergence_strength", 0.0)
        )
        cross_substrate_alignment = float(
            convergence.get("cross_substrate_alignment", 0.0)
        )
        universal_moral_similarity = float(
            convergence.get("universal_moral_similarity", 0.0)
        )
        moral_convergence_of_intelligences = bool(
            convergence.get("moral_convergence_of_intelligences", False)
        )

        # Moral objectivity emerges from convergence and similarity.
        ethical_objectivity_strength = self._clamp(
            (
                moral_convergence_strength
                + universal_moral_similarity
            )
            / 2.0
        )

        # Normativity is grounded in structural constraints when objective ethics
        # aligns across heterogeneous substrates.
        constraint_grounded_normativity = self._clamp(
            (
                ethical_objectivity_strength
                + cross_substrate_alignment
            )
            / 2.0
        )

        # Ethics becomes universal when constraint-grounded norms are shared.
        universality_of_ethics = self._clamp(
            (
                constraint_grounded_normativity
                + universal_moral_similarity
            )
            / 2.0
        )

        # Minimal threshold for robust universality.
        threshold = 0.50

        objective_ethics_under_constraints = (
            moral_convergence_of_intelligences
            and universality_of_ethics >= threshold
        )

        return {
            "ethical_objectivity_strength": ethical_objectivity_strength,
            "constraint_grounded_normativity": constraint_grounded_normativity,
            "universality_of_ethics": universality_of_ethics,
            "objective_ethics_under_constraints": (
                objective_ethics_under_constraints
            ),
            "principle": self.PRINCIPLE,
            "moral_convergence_of_intelligences_diagnostics": convergence,
        }


if __name__ == "__main__":
    primitive = ObjectiveEthicsUnderConstraintsPrimitive()

    print("\n--- objective ethics under constraints ---")
    pprint(primitive.step())
