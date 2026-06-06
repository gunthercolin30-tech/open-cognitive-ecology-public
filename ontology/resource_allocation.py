from __future__ import annotations

PRIMITIVE = "resource_allocation"
DESCRIPTION = "Resource allocation."
DEPENDENCIES = []

"""
RESOURCE_ALLOCATION primitive.

This module formalizes the distribution of limited resources across competing
demands. Resource allocation emerges from available resources, allocation
efficiency, and the degree to which prioritized needs are satisfied.

The primitive computes:
- resource_availability
- allocation_efficiency
- priority_satisfaction
- resource_allocation_index
"""


PRIMITIVE_NAME = "RESOURCE_ALLOCATION"
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


class ResourceAllocation:
    """Formal model of constrained resource distribution."""

    def __init__(
        self,
        availability_weight=1.0,
        efficiency_weight=1.0,
        satisfaction_weight=1.0,
    ):
        self.availability_weight = max(0.0, float(availability_weight))
        self.efficiency_weight = max(0.0, float(efficiency_weight))
        self.satisfaction_weight = max(0.0, float(satisfaction_weight))

    def evaluate(
        self,
        resource_availability=0.0,
        allocation_efficiency=0.0,
        priority_satisfaction=0.0,
    ):
        resource_availability = _clamp(resource_availability)
        allocation_efficiency = _clamp(allocation_efficiency)
        priority_satisfaction = _clamp(priority_satisfaction)

        total_weight = (
            self.availability_weight
            + self.efficiency_weight
            + self.satisfaction_weight
        )

        if total_weight <= 0.0:
            resource_allocation_index = 0.0
        else:
            resource_allocation_index = (
                self.availability_weight * resource_availability
                + self.efficiency_weight * allocation_efficiency
                + self.satisfaction_weight * priority_satisfaction
            ) / total_weight

        resource_allocation_index = _clamp(resource_allocation_index)

        is_empty = (
            resource_availability == 0.0
            and allocation_efficiency == 0.0
            and priority_satisfaction == 0.0
        )

        return {
            "resource_availability": resource_availability,
            "allocation_efficiency": allocation_efficiency,
            "priority_satisfaction": priority_satisfaction,
            "resource_allocation_index": resource_allocation_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "availability_weight": self.availability_weight,
                "efficiency_weight": self.efficiency_weight,
                "satisfaction_weight": self.satisfaction_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        resource_availability=0.0,
        allocation_efficiency=0.0,
        priority_satisfaction=0.0,
    ):
        return self.evaluate(
            resource_availability,
            allocation_efficiency,
            priority_satisfaction,
        )

    def validate(
        self,
        resource_availability=0.0,
        allocation_efficiency=0.0,
        priority_satisfaction=0.0,
    ):
        result = self.evaluate(
            resource_availability,
            allocation_efficiency,
            priority_satisfaction,
        )

        resource_allocation_index = result["resource_allocation_index"]

        return {
            "is_valid": resource_allocation_index > 0.0,
            "resource_allocation_index": resource_allocation_index,
            "diagnostics": result["diagnostics"],
        }
