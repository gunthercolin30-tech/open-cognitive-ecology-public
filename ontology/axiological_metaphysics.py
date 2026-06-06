from __future__ import annotations

PRIMITIVE = "axiological_metaphysics"
DESCRIPTION = "Axiological metaphysics."
DEPENDENCIES = []

"""
ontology/axiological_metaphysics.py

Formalization of the principle AXIOLOGICAL_METAPHYSICS.

This module expresses the idea that the metaphysical structure of reality is
intrinsically organized in axiological terms. Values are not external
annotations applied to an otherwise neutral ontology; they participate in the
fundamental architecture of being itself.

The primitive relies exclusively on OntologicalAxiologyPrimitive and derives
higher-level diagnostics describing the extent to which metaphysical reality is
grounded in objective structures of value.
"""


from pprint import pprint

from ontology.ontological_axiology import (
    OntologicalAxiologyPrimitive,
)


class AxiologicalMetaphysicsPrimitive:
    """
    Computational formalization of AXIOLOGICAL_METAPHYSICS.

    Principle
    ---------
    AXIOLOGICAL_METAPHYSICS states that the metaphysical structure of reality
    possesses an intrinsic axiological organization. Values are constitutive
    dimensions of being and participate directly in the foundational structure
    of the real.

    Derived Diagnostics
    -------------------
    metaphysical_axiological_structure:
        Degree to which the metaphysical structure of reality is axiologically
        organized.

    value_grounded_metaphysics:
        Degree to which metaphysics is grounded in structures of value.

    axiological_metaphysical_depth:
        Depth of the metaphysical embedding of axiological structure.

    axiological_metaphysics:
        Boolean indicating whether reality exhibits a constitutive axiological
        metaphysics.
    """

    PRINCIPLE = "AXIOLOGICAL_METAPHYSICS"

    # Minimal threshold above which axiological metaphysics is considered active.
    ACTIVATION_THRESHOLD = 0.5

    def __init__(self) -> None:
        self._ontological_axiology = OntologicalAxiologyPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """
        Clamp a numerical value to the interval [0.0, 1.0].
        """
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _combine(*values: float) -> float:
        """
        Combine normalized values by arithmetic averaging.

        Returns 0.0 if no values are provided.
        """
        if not values:
            return 0.0
        return sum(values) / len(values)

    def step(self) -> dict:
        """
        Execute one inference step for AXIOLOGICAL_METAPHYSICS.

        Returns
        -------
        dict
            Dictionary containing the derived diagnostics and the diagnostics
            of the underlying OntologicalAxiologyPrimitive.
        """
        base = self._ontological_axiology.step()

        axiological_ontological_status = self._clamp(
            base.get("axiological_ontological_status", 0.0)
        )
        normative_being_integration = self._clamp(
            base.get("normative_being_integration", 0.0)
        )
        axiological_foundational_depth = self._clamp(
            base.get("axiological_foundational_depth", 0.0)
        )
        ontological_axiology = bool(
            base.get("ontological_axiology", False)
        )

        # Degree to which metaphysical structure is intrinsically axiological.
        metaphysical_axiological_structure = self._clamp(
            self._combine(
                axiological_ontological_status,
                axiological_foundational_depth,
            )
        )

        # Degree to which metaphysics is grounded in structures of value.
        value_grounded_metaphysics = self._clamp(
            self._combine(
                metaphysical_axiological_structure,
                normative_being_integration,
            )
        )

        # Overall depth of the metaphysical embedding of axiological structure.
        axiological_metaphysical_depth = self._clamp(
            self._combine(
                value_grounded_metaphysics,
                axiological_foundational_depth,
            )
        )

        # Constitutive axiological metaphysics becomes active when the
        # underlying ontological axiology is established and sufficient depth
        # is reached.
        axiological_metaphysics = (
            ontological_axiology
            and axiological_metaphysical_depth >= self.ACTIVATION_THRESHOLD
        )

        return {
            "metaphysical_axiological_structure": (
                metaphysical_axiological_structure
            ),
            "value_grounded_metaphysics": value_grounded_metaphysics,
            "axiological_metaphysical_depth": (
                axiological_metaphysical_depth
            ),
            "axiological_metaphysics": axiological_metaphysics,
            "principle": self.PRINCIPLE,
            "ontological_axiology_diagnostics": base,
        }


if __name__ == "__main__":
    primitive = AxiologicalMetaphysicsPrimitive()

    print("\n--- axiological metaphysics ---")
    pprint(primitive.step())
