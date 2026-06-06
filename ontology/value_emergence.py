from __future__ import annotations

PRIMITIVE = "value_emergence"
DESCRIPTION = "Value emergence."
DEPENDENCIES = []

"""
ontology/value_emergence.py

Formalization of the principle VALUE_EMERGENCE.

This module expresses the idea that values are not absolute or transcendent
entities. Instead, they emerge locally from contextual, transient, and
revisable purposes.

The primitive is built directly on top of LocalPurposesPrimitive, which
establishes that teleological structures are local rather than globally fixed.

Principle
---------
VALUE_EMERGENCE

Interpretation
--------------
When contextual goals become sufficiently dense and persist in a revisable
manner, they generate local evaluative structures. These structures remain
provisional, context-dependent, and continuously open to revision.

Dependencies
------------
- ontology.local_purposes.LocalPurposesPrimitive
"""


from typing import Any, Dict

from ontology.local_purposes import (
    LocalPurposesPrimitive,
)

PRINCIPLE = "VALUE_EMERGENCE"


class ValueEmergencePrimitive:
    """
    Primitive implementing the VALUE_EMERGENCE principle.

    Values are modeled as emergent structures arising from local purposes.
    Their stability is temporary, and their persistence depends on continual
    revision rather than immutable foundations.
    """

    PRINCIPLE = PRINCIPLE

    def __init__(self) -> None:
        self.local_purposes_primitive = LocalPurposesPrimitive()

    def step(self) -> Dict[str, Any]:
        """
        Execute one diagnostic step.

        Returns
        -------
        dict
            Diagnostics describing the emergence and persistence of local
            values.
        """
        local_purposes_diagnostics = self.local_purposes_primitive.step()

        contextual_goal_density = float(
            local_purposes_diagnostics["contextual_goal_density"]
        )
        transient_purpose_stability = float(
            local_purposes_diagnostics["transient_purpose_stability"]
        )
        revisable_goal_persistence = float(
            local_purposes_diagnostics["revisable_goal_persistence"]
        )
        local_purposes = bool(
            local_purposes_diagnostics["local_purposes"]
        )

        # Intensity with which values are generated from local goals.
        contextual_value_generation = (
            contextual_goal_density + revisable_goal_persistence
        ) / 2.0

        # Temporary stability of emergent values.
        provisional_value_stability = (
            contextual_value_generation + transient_purpose_stability
        ) / 2.0

        # Persistence of values under continual revision.
        revisable_value_persistence = (
            provisional_value_stability + revisable_goal_persistence
        ) / 2.0

        # Local values are considered constituted when local purposes exist
        # and revisable persistence exceeds a minimal threshold.
        value_emergence = (
            local_purposes and revisable_value_persistence >= 0.5
        )

        return {
            "principle": self.PRINCIPLE,
            "local_purposes_diagnostics": local_purposes_diagnostics,
            "contextual_value_generation": contextual_value_generation,
            "provisional_value_stability": provisional_value_stability,
            "revisable_value_persistence": revisable_value_persistence,
            "value_emergence": value_emergence,
        }


if __name__ == "__main__":
    primitive = ValueEmergencePrimitive()
    diagnostics = primitive.step()

    print("\n--- value emergence ---")
    for key, value in diagnostics.items():
        print(f"{key}: {value}")
