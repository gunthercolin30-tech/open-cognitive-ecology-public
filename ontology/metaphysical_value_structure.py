from __future__ import annotations

PRIMITIVE = "metaphysical_value_structure"
DESCRIPTION = "Metaphysical value structure."
DEPENDENCIES = []

"""
ontology/metaphysical_value_structure.py

Formalization of the principle:

    METAPHYSICAL_VALUE_STRUCTURE

This module models the idea that values constitute a fundamental structural
dimension of metaphysical reality. Values are not secondary annotations of
existing entities; they participate directly in the constitutive organization
of being itself.

The implementation relies exclusively on:

    AxiologicalMetaphysicsPrimitive

which establishes that metaphysics is intrinsically grounded in axiological
structures.

Author: Colin Gunther
"""


from pprint import pprint
from typing import Any, Dict

from ontology.axiological_metaphysics import (
    AxiologicalMetaphysicsPrimitive,
)


class MetaphysicalValueStructurePrimitive:
    """
    Primitive formalizing the principle:

        METAPHYSICAL_VALUE_STRUCTURE

    The principle states that values form a structural layer of reality and
    that metaphysical organization is fundamentally shaped by axiological
    architecture.
    """

    PRINCIPLE = "METAPHYSICAL_VALUE_STRUCTURE"

    # Minimum depth required to consider values as a genuine metaphysical
    # structure.
    STRUCTURAL_DEPTH_THRESHOLD = 0.50

    def __init__(self) -> None:
        self.axiological_metaphysics = AxiologicalMetaphysicsPrimitive()

    @staticmethod
    def _clamp(value: Any) -> float:
        """
        Convert a value to float and clamp it to the [0, 1] interval.
        """
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0
        return max(0.0, min(1.0, value))

    @staticmethod
    def _mean(*values: Any) -> float:
        """
        Arithmetic mean over clamped values.
        """
        if not values:
            return 0.0
        normalized = [MetaphysicalValueStructurePrimitive._clamp(v) for v in values]
        return sum(normalized) / len(normalized)

    def step(self) -> Dict[str, Any]:
        """
        Compute diagnostics for the principle METAPHYSICAL_VALUE_STRUCTURE.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing:
                - fundamental_value_structure
                - metaphysical_value_foundation
                - value_structural_depth
                - metaphysical_value_structure
                - principle
                - axiological_metaphysics_diagnostics
        """
        diagnostics = self.axiological_metaphysics.step()

        metaphysical_axiological_structure = self._clamp(
            diagnostics.get("metaphysical_axiological_structure", 0.0)
        )
        value_grounded_metaphysics = self._clamp(
            diagnostics.get("value_grounded_metaphysics", 0.0)
        )
        axiological_metaphysical_depth = self._clamp(
            diagnostics.get("axiological_metaphysical_depth", 0.0)
        )
        axiological_metaphysics = bool(
            diagnostics.get("axiological_metaphysics", False)
        )

        # Degree to which values form a fundamental structure of reality.
        fundamental_value_structure = self._mean(
            metaphysical_axiological_structure,
            axiological_metaphysical_depth,
        )

        # Degree to which metaphysics is grounded in value structures.
        metaphysical_value_foundation = self._mean(
            fundamental_value_structure,
            value_grounded_metaphysics,
        )

        # Structural depth of the metaphysical value architecture.
        value_structural_depth = self._mean(
            metaphysical_value_foundation,
            axiological_metaphysical_depth,
        )

        # Boolean criterion for the existence of a metaphysical value structure.
        metaphysical_value_structure = (
            axiological_metaphysics
            and value_structural_depth >= self.STRUCTURAL_DEPTH_THRESHOLD
        )

        return {
            "principle": self.PRINCIPLE,
            "fundamental_value_structure": fundamental_value_structure,
            "metaphysical_value_foundation": metaphysical_value_foundation,
            "value_structural_depth": value_structural_depth,
            "metaphysical_value_structure": metaphysical_value_structure,
            "axiological_metaphysics_diagnostics": diagnostics,
        }


if __name__ == "__main__":
    primitive = MetaphysicalValueStructurePrimitive()

    print("\n--- metaphysical value structure ---")
    pprint(primitive.step())
