from __future__ import annotations

PRIMITIVE = "ontological_axiology"
DESCRIPTION = "Ontological axiology."
DEPENDENCIES = []

"""
ontology/ontological_axiology.py

Formalisation of the principle ONTOLOGICAL_AXIOLOGY.

This module expresses the idea that axiological structure is not merely
objective, but constitutes a fundamental ontological dimension of reality.
Values are treated as structurally integrated with being itself and therefore
participate in the foundational architecture of existence.

The implementation relies exclusively on ObjectiveAxiologyPrimitive.
"""


from pprint import pprint
from typing import Any, Dict

from ontology.objective_axiology import (
    ObjectiveAxiologyPrimitive,
)

PRINCIPLE = "ONTOLOGICAL_AXIOLOGY"


class OntologicalAxiologyPrimitive:
    """
    ONTOLOGICAL_AXIOLOGY

    Formalizes the principle that axiological structure belongs to the ontology
    of reality itself.

    Interpretation:
        - Values are not subjective projections.
        - Normativity is objectively structured.
        - Objective value structure is integrated into being.
        - Axiology has foundational ontological significance.

    Expected diagnostics:
        - axiological_ontological_status
        - normative_being_integration
        - axiological_foundational_depth
        - ontological_axiology
    """

    PRINCIPLE = PRINCIPLE

    def __init__(
        self,
        objective_axiology: ObjectiveAxiologyPrimitive | None = None,
        foundational_threshold: float = 0.50,
    ) -> None:
        """
        Initialize the primitive.

        Args:
            objective_axiology:
                Optional preconfigured ObjectiveAxiologyPrimitive.
            foundational_threshold:
                Minimum axiological_foundational_depth required to assert that
                axiological structure constitutes a fundamental ontological
                dimension of reality.
        """
        self.objective_axiology = (
            objective_axiology
            if objective_axiology is not None
            else ObjectiveAxiologyPrimitive()
        )
        self.foundational_threshold = float(foundational_threshold)

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a numeric value to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one evaluation step.

        Returns:
            Dictionary containing ontological axiology diagnostics.
        """
        objective_diag = self.objective_axiology.step()

        axiological_domain_objectivity = self._clamp(
            objective_diag.get("axiological_domain_objectivity", 0.0)
        )
        objective_normative_structure = self._clamp(
            objective_diag.get("objective_normative_structure", 0.0)
        )
        axiological_reality_strength = self._clamp(
            objective_diag.get("axiological_reality_strength", 0.0)
        )
        objective_axiology = bool(
            objective_diag.get("objective_axiology", False)
        )

        # Degree to which axiological structure possesses ontological status.
        axiological_ontological_status = self._clamp(
            (
                axiological_domain_objectivity
                + axiological_reality_strength
            ) / 2.0
        )

        # Degree of integration between being and normativity.
        normative_being_integration = self._clamp(
            (
                axiological_ontological_status
                + objective_normative_structure
            ) / 2.0
        )

        # Foundational depth of the axiological dimension.
        axiological_foundational_depth = self._clamp(
            (
                normative_being_integration
                + axiological_reality_strength
            ) / 2.0
        )

        # The axiological domain is recognized as ontologically fundamental.
        ontological_axiology = (
            objective_axiology
            and axiological_foundational_depth >= self.foundational_threshold
        )

        return {
            "principle": self.PRINCIPLE,
            "objective_axiology_diagnostics": objective_diag,
            "axiological_ontological_status": axiological_ontological_status,
            "normative_being_integration": normative_being_integration,
            "axiological_foundational_depth": axiological_foundational_depth,
            "ontological_axiology": ontological_axiology,
        }


if __name__ == "__main__":
    primitive = OntologicalAxiologyPrimitive()

    print("\n--- ontological axiology ---")
    pprint(primitive.step())
