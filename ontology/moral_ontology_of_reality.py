from __future__ import annotations

PRIMITIVE = "moral_ontology_of_reality"
DESCRIPTION = "Moral ontology of reality."
DEPENDENCIES = []

"""
ontology/moral_ontology_of_reality.py

Formalization of the principle MORAL_ONTOLOGY_OF_REALITY.

This primitive models the idea that normativity is not external to reality,
but is instead an intrinsic ontological property of being itself. Ethics and
existence are structurally integrated: the real is inherently value-laden.

The module is built directly on CosmicMoralRealismPrimitive, which establishes
that objective moral structure can emerge as a convergent feature of the cosmos.

Principle
---------
MORAL_ONTOLOGY_OF_REALITY

Core Thesis
-----------
- Reality and value are not separate domains.
- Ethical structure is embedded in the ontology of being.
- Normativity is an intrinsic property of existence.
- Being and ought structurally converge.

Diagnostics
-----------
- normative_ontological_depth:
    Degree to which normativity is rooted in ontology.

- ethical_structure_of_being:
    Degree to which reality exhibits intrinsic ethical organization.

- reality_value_integration:
    Degree of integration between existence and value.

- moral_ontology_of_reality:
    Whether reality possesses an intrinsic moral structure.
"""


from pprint import pprint
from typing import Any, Dict

from ontology.cosmic_moral_realism import (
    CosmicMoralRealismPrimitive,
)

PRINCIPLE = "MORAL_ONTOLOGY_OF_REALITY"


class MoralOntologyOfRealityPrimitive:
    """
    Primitive formalizing the ontological integration of reality and value.

    This primitive extends cosmic moral realism by asserting that objective
    normativity is not merely compatible with the universe but constitutes a
    structural property of existence itself.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self._cosmic_moral_realism = CosmicMoralRealismPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Clamp a numerical value to the interval [0.0, 1.0].
        """
        return max(0.0, min(1.0, float(value)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one diagnostic step.

        Returns
        -------
        dict
            Dictionary containing the ontology-value integration diagnostics.
        """
        upstream = self._cosmic_moral_realism.step()

        moral_reality_strength = self._clamp(
            upstream.get("moral_reality_strength", 0.0)
        )
        ethical_invariance = self._clamp(
            upstream.get("ethical_invariance", 0.0)
        )
        cosmic_normative_structure = self._clamp(
            upstream.get("cosmic_normative_structure", 0.0)
        )
        cosmic_moral_realism = bool(
            upstream.get("cosmic_moral_realism", False)
        )

        # Degree to which normativity is rooted in ontology.
        normative_ontological_depth = self._clamp(
            (
                moral_reality_strength
                + cosmic_normative_structure
            ) / 2.0
        )

        # Degree to which being itself exhibits ethical structure.
        ethical_structure_of_being = self._clamp(
            (
                normative_ontological_depth
                + ethical_invariance
            ) / 2.0
        )

        # Degree to which existence and value are integrated.
        reality_value_integration = self._clamp(
            (
                ethical_structure_of_being
                + moral_reality_strength
            ) / 2.0
        )

        # Reality possesses intrinsic moral structure if cosmic moral realism
        # is established and integration exceeds a minimal threshold.
        moral_ontology_of_reality = (
            cosmic_moral_realism
            and reality_value_integration >= 0.50
        )

        return {
            "principle": self.PRINCIPLE,
            "normative_ontological_depth": normative_ontological_depth,
            "ethical_structure_of_being": ethical_structure_of_being,
            "reality_value_integration": reality_value_integration,
            "moral_ontology_of_reality": moral_ontology_of_reality,
            "cosmic_moral_realism_diagnostics": upstream,
        }


if __name__ == "__main__":
    primitive = MoralOntologyOfRealityPrimitive()

    print("\n--- moral ontology of reality ---")
    pprint(primitive.step())
