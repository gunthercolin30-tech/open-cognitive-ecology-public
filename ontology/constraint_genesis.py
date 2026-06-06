from __future__ import annotations

PRIMITIVE = "constraint_genesis"
DESCRIPTION = "Constraint genesis."
DEPENDENCIES = []

"""
CONSTRAINT_GENESIS primitive.

This module formalizes the emergence of new constraints that restructure the
space of viable possibilities. Constraint genesis integrates novel constraint
emergence, structural stabilization, and possibility reconfiguration.

The primitive computes:
- novel_constraint_emergence
- structural_stabilization
- possibility_reconfiguration
- constraint_genesis_index
"""


PRIMITIVE_NAME = "CONSTRAINT_GENESIS"
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


class ConstraintGenesis:
    """Formal model of the emergence of new structuring constraints."""

    def __init__(
        self,
        emergence_weight=1.0,
        stabilization_weight=1.0,
        reconfiguration_weight=1.0,
    ):
        self.emergence_weight = max(0.0, float(emergence_weight))
        self.stabilization_weight = max(0.0, float(stabilization_weight))
        self.reconfiguration_weight = max(
            0.0, float(reconfiguration_weight)
        )

    def evaluate(
        self,
        novel_constraint_emergence=0.0,
        structural_stabilization=0.0,
        possibility_reconfiguration=0.0,
    ):
        novel_constraint_emergence = _clamp(
            novel_constraint_emergence
        )
        structural_stabilization = _clamp(
            structural_stabilization
        )
        possibility_reconfiguration = _clamp(
            possibility_reconfiguration
        )

        total_weight = (
            self.emergence_weight
            + self.stabilization_weight
            + self.reconfiguration_weight
        )

        if total_weight <= 0.0:
            constraint_genesis_index = 0.0
        else:
            constraint_genesis_index = (
                self.emergence_weight
                * novel_constraint_emergence
                + self.stabilization_weight
                * structural_stabilization
                + self.reconfiguration_weight
                * possibility_reconfiguration
            ) / total_weight

        constraint_genesis_index = _clamp(
            constraint_genesis_index
        )

        is_empty = (
            novel_constraint_emergence == 0.0
            and structural_stabilization == 0.0
            and possibility_reconfiguration == 0.0
        )

        return {
            "novel_constraint_emergence":
                novel_constraint_emergence,
            "structural_stabilization":
                structural_stabilization,
            "possibility_reconfiguration":
                possibility_reconfiguration,
            "constraint_genesis_index":
                constraint_genesis_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "emergence_weight": self.emergence_weight,
                "stabilization_weight":
                    self.stabilization_weight,
                "reconfiguration_weight":
                    self.reconfiguration_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        novel_constraint_emergence=0.0,
        structural_stabilization=0.0,
        possibility_reconfiguration=0.0,
    ):
        return self.evaluate(
            novel_constraint_emergence,
            structural_stabilization,
            possibility_reconfiguration,
        )

    def validate(
        self,
        novel_constraint_emergence=0.0,
        structural_stabilization=0.0,
        possibility_reconfiguration=0.0,
    ):
        result = self.evaluate(
            novel_constraint_emergence,
            structural_stabilization,
            possibility_reconfiguration,
        )

        index_ = result["constraint_genesis_index"]

        return {
            "is_valid": index_ > 0.0,
            "constraint_genesis_index": index_,
            "diagnostics": result["diagnostics"],
        }
