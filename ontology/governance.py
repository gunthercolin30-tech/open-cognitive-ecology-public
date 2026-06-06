from __future__ import annotations

PRIMITIVE = "governance"
DESCRIPTION = "Governance."
DEPENDENCIES = []

"""
GOVERNANCE primitive.

This module formalizes governance as the capacity of a collective to coordinate
behavior, maintain normative legitimacy, and manage shared resources under
constraints.

The primitive computes:
- coordination_capacity
- normative_legitimacy
- resource_management
- governance_index
"""


PRIMITIVE_NAME = "GOVERNANCE"
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


class Governance:
    """Formal model of collective governance under constraints."""

    def __init__(
        self,
        coordination_weight=1.0,
        legitimacy_weight=1.0,
        management_weight=1.0,
    ):
        self.coordination_weight = max(0.0, float(coordination_weight))
        self.legitimacy_weight = max(0.0, float(legitimacy_weight))
        self.management_weight = max(0.0, float(management_weight))

    def evaluate(
        self,
        coordination_capacity=0.0,
        normative_legitimacy=0.0,
        resource_management=0.0,
    ):
        coordination_capacity = _clamp(coordination_capacity)
        normative_legitimacy = _clamp(normative_legitimacy)
        resource_management = _clamp(resource_management)

        total_weight = (
            self.coordination_weight
            + self.legitimacy_weight
            + self.management_weight
        )

        if total_weight <= 0.0:
            governance_index = 0.0
        else:
            governance_index = (
                self.coordination_weight * coordination_capacity
                + self.legitimacy_weight * normative_legitimacy
                + self.management_weight * resource_management
            ) / total_weight

        governance_index = _clamp(governance_index)

        is_empty = (
            coordination_capacity == 0.0
            and normative_legitimacy == 0.0
            and resource_management == 0.0
        )

        return {
            "coordination_capacity": coordination_capacity,
            "normative_legitimacy": normative_legitimacy,
            "resource_management": resource_management,
            "governance_index": governance_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "coordination_weight": self.coordination_weight,
                "legitimacy_weight": self.legitimacy_weight,
                "management_weight": self.management_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        coordination_capacity=0.0,
        normative_legitimacy=0.0,
        resource_management=0.0,
    ):
        return self.evaluate(
            coordination_capacity,
            normative_legitimacy,
            resource_management,
        )

    def validate(
        self,
        coordination_capacity=0.0,
        normative_legitimacy=0.0,
        resource_management=0.0,
    ):
        result = self.evaluate(
            coordination_capacity,
            normative_legitimacy,
            resource_management,
        )

        governance_index = result["governance_index"]

        return {
            "is_valid": governance_index > 0.0,
            "governance_index": governance_index,
            "diagnostics": result["diagnostics"],
        }
