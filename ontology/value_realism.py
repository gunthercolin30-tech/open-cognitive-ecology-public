from __future__ import annotations

PRIMITIVE = "value_realism"
DESCRIPTION = "Value realism."
DEPENDENCIES = []

"""
ontology/value_realism.py

Formalization of the principle VALUE_REALISM.

This module expresses the idea that values are objective features of reality.
They do not depend on subjective preferences, social conventions, or arbitrary
projections, but are grounded in the intrinsic axiological structure of being.

The implementation relies exclusively on:

    AxiologicalStructureOfBeingPrimitive

which evaluates whether value is intrinsically embedded in existence itself.

Principle
---------
VALUE_REALISM:
    Values are real, objective, and mind-independent aspects of being.

Interpretation
--------------
If existence possesses intrinsic axiological density and coherent value
organization, then values are not merely subjective constructions but genuine
ontological structures.

Returned diagnostics
--------------------
objective_value_presence:
    Degree to which objective value is present in reality.

mind_independent_value_reality:
    Degree to which value exists independently of any observer.

value_structure_objectivity:
    Degree to which the axiological organization is objectively robust.

value_realism:
    True when values are objectively real.
"""


from pprint import pprint

from ontology.axiological_structure_of_being import (
    AxiologicalStructureOfBeingPrimitive,
)


class ValueRealismPrimitive:
    """
    Primitive implementing the principle VALUE_REALISM.

    Values are treated as objective and mind-independent structures when the
    axiological structure of being is sufficiently dense and coherent.
    """

    PRINCIPLE = "VALUE_REALISM"

    def __init__(self) -> None:
        self.axiological_structure_of_being = (
            AxiologicalStructureOfBeingPrimitive()
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a scalar into the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics characterizing the ontological reality of values.
        """
        diagnostics = self.axiological_structure_of_being.step()

        axiological_density_of_being = self._clamp(
            diagnostics.get("axiological_density_of_being", 0.0)
        )
        value_intrinsic_to_existence = self._clamp(
            diagnostics.get("value_intrinsic_to_existence", 0.0)
        )
        ontological_value_coherence = self._clamp(
            diagnostics.get("ontological_value_coherence", 0.0)
        )
        axiological_structure_of_being = bool(
            diagnostics.get("axiological_structure_of_being", False)
        )

        # Degree to which objective value is effectively present in reality.
        objective_value_presence = self._clamp(
            0.5 * axiological_density_of_being
            + 0.5 * value_intrinsic_to_existence
        )

        # Degree to which value exists independently of observers.
        mind_independent_value_reality = self._clamp(
            0.5 * objective_value_presence
            + 0.5 * ontological_value_coherence
        )

        # Robustness of the objective axiological structure.
        value_structure_objectivity = self._clamp(
            0.5 * mind_independent_value_reality
            + 0.5 * ontological_value_coherence
        )

        # Values are considered objectively real if the underlying axiological
        # structure exists and its objectivity exceeds a minimal threshold.
        value_realism = (
            axiological_structure_of_being
            and value_structure_objectivity >= 0.50
        )

        return {
            "principle": self.PRINCIPLE,
            "objective_value_presence": objective_value_presence,
            "mind_independent_value_reality": (
                mind_independent_value_reality
            ),
            "value_structure_objectivity": (
                value_structure_objectivity
            ),
            "value_realism": value_realism,
            "axiological_structure_of_being_diagnostics": diagnostics,
        }


if __name__ == "__main__":
    primitive = ValueRealismPrimitive()

    print("\n--- value realism ---")
    pprint(primitive.step())
