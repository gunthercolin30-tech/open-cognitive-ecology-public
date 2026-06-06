from __future__ import annotations

PRIMITIVE = "axiological_structure_of_being"
DESCRIPTION = "Axiological structure of being."
DEPENDENCIES = []

"""
ontology/axiological_structure_of_being.py

Formalizes the principle AXIOLOGICAL_STRUCTURE_OF_BEING.

The purpose of this module is to express the idea that being possesses an
intrinsic axiological structure. Value is not externally projected onto
reality by observers; rather, value constitutes a fundamental dimension of
existence itself.

This primitive is built directly upon MoralOntologyOfRealityPrimitive,
which establishes that reality is intrinsically normatively structured.

Principle
---------
AXIOLOGICAL_STRUCTURE_OF_BEING

Core Idea
---------
If reality possesses an inherent moral ontology, then being itself contains
an intrinsic density of value. Existence is not axiologically neutral.
Values are constitutive properties of the ontological domain.

Returned Diagnostics
--------------------
- axiological_density_of_being
- value_intrinsic_to_existence
- ontological_value_coherence
- axiological_structure_of_being
"""


from pprint import pprint
from typing import Any, Dict

from ontology.moral_ontology_of_reality import (
    MoralOntologyOfRealityPrimitive,
)


class AxiologicalStructureOfBeingPrimitive:
    """
    Primitive formalizing AXIOLOGICAL_STRUCTURE_OF_BEING.

    This primitive models the thesis that being possesses an intrinsic
    value-structure. Ontology and axiology are not separate domains:
    value is embedded in the very constitution of reality.
    """

    PRINCIPLE = "AXIOLOGICAL_STRUCTURE_OF_BEING"

    def __init__(
        self,
        moral_ontology_of_reality: MoralOntologyOfRealityPrimitive | None = None,
        coherence_threshold: float = 0.50,
    ) -> None:
        """
        Initialize the primitive.

        Parameters
        ----------
        moral_ontology_of_reality:
            Optional preconfigured MoralOntologyOfRealityPrimitive.
        coherence_threshold:
            Minimum coherence required to affirm that being possesses an
            intrinsic axiological structure.
        """
        self.moral_ontology_of_reality = (
            moral_ontology_of_reality
            if moral_ontology_of_reality is not None
            else MoralOntologyOfRealityPrimitive()
        )
        self.coherence_threshold = float(coherence_threshold)

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a numeric value to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _average(*values: float) -> float:
        """Compute the arithmetic mean of values, clamped to [0.0, 1.0]."""
        if not values:
            return 0.0
        return max(0.0, min(1.0, sum(values) / len(values)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics establishing whether value is intrinsic to being.
        """
        moral = self.moral_ontology_of_reality.step()

        normative_ontological_depth = self._clamp(
            moral.get("normative_ontological_depth", 0.0)
        )
        ethical_structure_of_being = self._clamp(
            moral.get("ethical_structure_of_being", 0.0)
        )
        reality_value_integration = self._clamp(
            moral.get("reality_value_integration", 0.0)
        )
        moral_ontology_of_reality = bool(
            moral.get("moral_ontology_of_reality", False)
        )

        # Density of intrinsic value within being.
        axiological_density_of_being = self._average(
            normative_ontological_depth,
            reality_value_integration,
        )

        # Degree to which value is constitutive of existence.
        value_intrinsic_to_existence = self._average(
            axiological_density_of_being,
            ethical_structure_of_being,
        )

        # Consistency between ontology and axiology.
        ontological_value_coherence = self._average(
            value_intrinsic_to_existence,
            reality_value_integration,
        )

        # Final determination.
        axiological_structure_of_being = (
            moral_ontology_of_reality
            and ontological_value_coherence >= self.coherence_threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "axiological_density_of_being": axiological_density_of_being,
            "value_intrinsic_to_existence": value_intrinsic_to_existence,
            "ontological_value_coherence": ontological_value_coherence,
            "axiological_structure_of_being": axiological_structure_of_being,
            "moral_ontology_of_reality_diagnostics": moral,
        }


if __name__ == "__main__":
    primitive = AxiologicalStructureOfBeingPrimitive()

    print("\n--- axiological structure of being ---")
    pprint(primitive.step())
