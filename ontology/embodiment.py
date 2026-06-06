from __future__ import annotations

PRIMITIVE = "embodiment"
DESCRIPTION = "Embodiment."
DEPENDENCIES = []

"""
EMBODIMENT primitive.

This module formalizes embodiment as the structural grounding of cognition in a
physical substrate. Embodiment emerges from sensorimotor coupling, integration
of physical constraints, and effective environmental grounding.

The primitive computes:
- sensorimotor_coupling
- physical_constraint_integration
- environmental_grounding
- embodiment_index
"""


PRIMITIVE_NAME = "EMBODIMENT"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


class Embodiment:
    """Formal model of cognition grounded in a physical substrate."""

    def __init__(
        self,
        coupling_weight=1.0,
        constraint_weight=1.0,
        grounding_weight=1.0,
    ):
        self.coupling_weight = max(0.0, float(coupling_weight))
        self.constraint_weight = max(0.0, float(constraint_weight))
        self.grounding_weight = max(0.0, float(grounding_weight))

    def evaluate(
        self,
        sensorimotor_coupling=0.0,
        physical_constraint_integration=0.0,
        environmental_grounding=0.0,
    ):
        sensorimotor_coupling = _clamp(sensorimotor_coupling)
        physical_constraint_integration = _clamp(
            physical_constraint_integration
        )
        environmental_grounding = _clamp(environmental_grounding)

        total_weight = (
            self.coupling_weight
            + self.constraint_weight
            + self.grounding_weight
        )

        if total_weight <= 0.0:
            embodiment_index = 0.0
        else:
            embodiment_index = (
                self.coupling_weight * sensorimotor_coupling
                + self.constraint_weight * physical_constraint_integration
                + self.grounding_weight * environmental_grounding
            ) / total_weight

        embodiment_index = _clamp(embodiment_index)

        is_empty = (
            sensorimotor_coupling == 0.0
            and physical_constraint_integration == 0.0
            and environmental_grounding == 0.0
        )

        return {
            "sensorimotor_coupling": sensorimotor_coupling,
            "physical_constraint_integration":
                physical_constraint_integration,
            "environmental_grounding": environmental_grounding,
            "embodiment_index": embodiment_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "coupling_weight": self.coupling_weight,
                "constraint_weight": self.constraint_weight,
                "grounding_weight": self.grounding_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        sensorimotor_coupling=0.0,
        physical_constraint_integration=0.0,
        environmental_grounding=0.0,
    ):
        return self.evaluate(
            sensorimotor_coupling,
            physical_constraint_integration,
            environmental_grounding,
        )

    def validate(
        self,
        sensorimotor_coupling=0.0,
        physical_constraint_integration=0.0,
        environmental_grounding=0.0,
    ):
        result = self.evaluate(
            sensorimotor_coupling,
            physical_constraint_integration,
            environmental_grounding,
        )

        embodiment_index = result["embodiment_index"]

        return {
            "is_valid": embodiment_index > 0.0,
            "embodiment_index": embodiment_index,
            "diagnostics": result["diagnostics"],
        }
