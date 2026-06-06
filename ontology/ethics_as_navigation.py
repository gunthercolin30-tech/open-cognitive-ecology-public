from __future__ import annotations

PRIMITIVE = "ethics_as_navigation"
DESCRIPTION = "Ethics as navigation."
DEPENDENCIES = []

"""
ontology.ethics_as_navigation
=============================

Formalizes the principle ETHICS_AS_NAVIGATION.

This module expresses the idea that ethics is not the application of fixed,
transcendent, or absolute values. Instead, ethics is modeled as an adaptive
navigation process within a field of values that are:

- contextually generated,
- provisionally stabilized,
- locally operative,
- revisable over time.

The resulting ethical dynamics depend on the emergence of local value
structures and on the capacity to evaluate and orient actions within those
structures.

Primitive implemented
---------------------
ETHICS_AS_NAVIGATION

Underlying primitive
--------------------
VALUE_EMERGENCE
"""


from pprint import pprint
from typing import Any, Dict

from ontology.value_emergence import (
    ValueEmergencePrimitive,
)


class EthicsAsNavigationPrimitive:
    """
    Primitive implementing ETHICS_AS_NAVIGATION.

    Ethics is treated as an adaptive navigation process inside a locally
    emergent and revisable value field rather than as obedience to absolute
    normative rules.
    """

    PRINCIPLE = "ETHICS_AS_NAVIGATION"

    def __init__(self) -> None:
        self.value_emergence = ValueEmergencePrimitive()

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a numeric value to the interval [0.0, 1.0]."""
        return max(0.0, min(1.0, float(value)))

    def step(self) -> Dict[str, Any]:
        """
        Execute one step of the ETHICS_AS_NAVIGATION primitive.

        Returns
        -------
        dict
            Diagnostics describing the emergence of ethical navigation.
        """
        value_emergence_diagnostics = self.value_emergence.step()

        contextual_value_generation = self._clamp(
            value_emergence_diagnostics.get(
                "contextual_value_generation",
                0.0,
            )
        )
        provisional_value_stability = self._clamp(
            value_emergence_diagnostics.get(
                "provisional_value_stability",
                0.0,
            )
        )
        revisable_value_persistence = self._clamp(
            value_emergence_diagnostics.get(
                "revisable_value_persistence",
                0.0,
            )
        )
        value_emergence = bool(
            value_emergence_diagnostics.get(
                "value_emergence",
                False,
            )
        )

        # Density of the local value field generated and maintained over time.
        value_field_density = self._clamp(
            (
                contextual_value_generation
                + revisable_value_persistence
            )
            / 2.0
        )

        # Capacity to orient within the value field using provisional
        # stabilizations.
        ethical_navigation_capacity = self._clamp(
            (
                value_field_density
                + provisional_value_stability
            )
            / 2.0
        )

        # Quality of context-sensitive and revisable evaluation.
        context_sensitive_evaluation = self._clamp(
            (
                ethical_navigation_capacity
                + revisable_value_persistence
            )
            / 2.0
        )

        # Minimal threshold required for effective ethical operation.
        ethics_as_navigation = bool(
            value_emergence
            and context_sensitive_evaluation >= 0.60
        )

        return {
            "principle": self.PRINCIPLE,
            "value_emergence_diagnostics": value_emergence_diagnostics,
            "value_field_density": value_field_density,
            "ethical_navigation_capacity": ethical_navigation_capacity,
            "context_sensitive_evaluation": context_sensitive_evaluation,
            "ethics_as_navigation": ethics_as_navigation,
        }


if __name__ == "__main__":
    primitive = EthicsAsNavigationPrimitive()
    diagnostics = primitive.step()

    print("\n--- ethics as navigation ---")
    pprint(diagnostics)
