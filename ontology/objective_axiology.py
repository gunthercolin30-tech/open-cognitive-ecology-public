from __future__ import annotations

PRIMITIVE = "objective_axiology"
DESCRIPTION = "Objective axiology."
DEPENDENCIES = []

"""
ontology/objective_axiology.py

Formalizes the principle OBJECTIVE_AXIOLOGY.

This module expresses the idea that axiology is an objective and structured
dimension of reality rather than a purely subjective construction.

The implementation is grounded directly in ValueRealismPrimitive, which
establishes that values exist objectively, independently of particular minds,
and possess an intrinsic structural organization.

Principle
---------
OBJECTIVE_AXIOLOGY

Interpretation
--------------
If values are objectively present, mind-independent, and structurally organized,
then the axiological domain itself constitutes a real ontological layer of the
universe. Normativity is therefore not externally imposed but emerges as an
intrinsic feature of reality.
"""


from pprint import pprint

from ontology.value_realism import (
    ValueRealismPrimitive,
)


PRINCIPLE = "OBJECTIVE_AXIOLOGY"


class ObjectiveAxiologyPrimitive:
    """
    Primitive formalizing OBJECTIVE_AXIOLOGY.

    Diagnostics
    -----------
    axiological_domain_objectivity:
        Degree to which the axiological domain possesses autonomous objectivity.

    objective_normative_structure:
        Strength of the objective normative structure inherent to reality.

    axiological_reality_strength:
        Ontological solidity of axiology as a real domain.

    objective_axiology:
        True when axiology constitutes an objective structure of reality.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self.value_realism = ValueRealismPrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a scalar to the [0.0, 1.0] interval."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> dict:
        """
        Execute one evaluation step.

        Returns
        -------
        dict
            Diagnostics characterizing the ontological objectivity of axiology.
        """
        value_realism_diagnostics = self.value_realism.step()

        objective_value_presence = self._clamp(
            value_realism_diagnostics.get("objective_value_presence", 0.0)
        )
        mind_independent_value_reality = self._clamp(
            value_realism_diagnostics.get("mind_independent_value_reality", 0.0)
        )
        value_structure_objectivity = self._clamp(
            value_realism_diagnostics.get("value_structure_objectivity", 0.0)
        )
        value_realism = bool(
            value_realism_diagnostics.get("value_realism", False)
        )

        # Degree to which the axiological domain possesses autonomous objectivity.
        axiological_domain_objectivity = self._clamp(
            (
                objective_value_presence
                + mind_independent_value_reality
            ) / 2.0
        )

        # Strength of the objective normative structure.
        objective_normative_structure = self._clamp(
            (
                axiological_domain_objectivity
                + value_structure_objectivity
            ) / 2.0
        )

        # Ontological solidity of axiology as a real domain.
        axiological_reality_strength = self._clamp(
            (
                objective_normative_structure
                + value_structure_objectivity
            ) / 2.0
        )

        # Axiology is objective if value realism holds and the resulting
        # ontological strength exceeds a minimal threshold.
        objective_axiology = (
            value_realism
            and axiological_reality_strength >= 0.50
        )

        return {
            "principle": self.PRINCIPLE,
            "value_realism_diagnostics": value_realism_diagnostics,
            "axiological_domain_objectivity": axiological_domain_objectivity,
            "objective_normative_structure": objective_normative_structure,
            "axiological_reality_strength": axiological_reality_strength,
            "objective_axiology": objective_axiology,
        }


if __name__ == "__main__":
    primitive = ObjectiveAxiologyPrimitive()

    print("\n--- objective axiology ---")
    pprint(primitive.step())
