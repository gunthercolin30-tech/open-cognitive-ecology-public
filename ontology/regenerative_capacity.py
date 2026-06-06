from __future__ import annotations

PRIMITIVE = "regenerative_capacity"
DESCRIPTION = "Regenerative capacity."
DEPENDENCIES = []

"""
REGENERATIVE_CAPACITY primitive.

This module formalizes the ability of a biological, ecological, or
civilizational system to restore the resources and functional structures
required for continued viability.

The primitive computes:
- resource_restoration
- functional_recovery
- renewal_sustainability
- regenerative_capacity_index
"""


PRIMITIVE_NAME = "REGENERATIVE_CAPACITY"
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


class RegenerativeCapacity:
    """Formal model of structural and resource regeneration."""

    def __init__(
        self,
        restoration_weight=1.0,
        recovery_weight=1.0,
        sustainability_weight=1.0,
    ):
        self.restoration_weight = max(0.0, float(restoration_weight))
        self.recovery_weight = max(0.0, float(recovery_weight))
        self.sustainability_weight = max(
            0.0, float(sustainability_weight)
        )

    def evaluate(
        self,
        resource_restoration=0.0,
        functional_recovery=0.0,
        renewal_sustainability=0.0,
    ):
        resource_restoration = _clamp(resource_restoration)
        functional_recovery = _clamp(functional_recovery)
        renewal_sustainability = _clamp(renewal_sustainability)

        total_weight = (
            self.restoration_weight
            + self.recovery_weight
            + self.sustainability_weight
        )

        if total_weight <= 0.0:
            regenerative_capacity_index = 0.0
        else:
            regenerative_capacity_index = (
                self.restoration_weight * resource_restoration
                + self.recovery_weight * functional_recovery
                + self.sustainability_weight * renewal_sustainability
            ) / total_weight

        regenerative_capacity_index = _clamp(
            regenerative_capacity_index
        )

        is_empty = (
            resource_restoration == 0.0
            and functional_recovery == 0.0
            and renewal_sustainability == 0.0
        )

        return {
            "resource_restoration": resource_restoration,
            "functional_recovery": functional_recovery,
            "renewal_sustainability": renewal_sustainability,
            "regenerative_capacity_index":
                regenerative_capacity_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "restoration_weight": self.restoration_weight,
                "recovery_weight": self.recovery_weight,
                "sustainability_weight":
                    self.sustainability_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        resource_restoration=0.0,
        functional_recovery=0.0,
        renewal_sustainability=0.0,
    ):
        return self.evaluate(
            resource_restoration,
            functional_recovery,
            renewal_sustainability,
        )

    def validate(
        self,
        resource_restoration=0.0,
        functional_recovery=0.0,
        renewal_sustainability=0.0,
    ):
        result = self.evaluate(
            resource_restoration,
            functional_recovery,
            renewal_sustainability,
        )

        index_ = result["regenerative_capacity_index"]

        return {
            "is_valid": index_ > 0.0,
            "regenerative_capacity_index": index_,
            "diagnostics": result["diagnostics"],
        }
