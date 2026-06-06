PRIMITIVE = "carrying_capacity"
DESCRIPTION = "Carrying capacity."
DEPENDENCIES = []

"""
CARRYING_CAPACITY
=================

This primitive formalizes carrying capacity as the maximum sustainable load that
an ecological system can support without structural degradation.

The carrying capacity index integrates three bounded components:

- resource_availability: amount of accessible resources.
- regeneration_rate: rate at which resources are renewed.
- population_pressure: intensity of demand placed on the system.

High resource availability and regeneration increase carrying capacity, whereas
high population pressure decreases it.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "CARRYING_CAPACITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class CarryingCapacity:
    """Quantifies carrying capacity as a bounded index in [0, 1]."""

    def __init__(
        self,
        resource_weight: float = 1.0,
        regeneration_weight: float = 1.0,
        pressure_weight: float = 1.0,
    ) -> None:
        self.resource_weight = max(0.0, float(resource_weight))
        self.regeneration_weight = max(0.0, float(regeneration_weight))
        self.pressure_weight = max(0.0, float(pressure_weight))

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except (TypeError, ValueError):
            return 0.0
        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return x

    def evaluate(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if inputs is None:
            inputs = {}

        resource_availability = self._clamp(
            inputs.get("resource_availability", 0.0)
        )
        regeneration_rate = self._clamp(
            inputs.get("regeneration_rate", 0.0)
        )
        population_pressure = self._clamp(
            inputs.get("population_pressure", 0.0)
        )

        total_weight = (
            self.resource_weight
            + self.regeneration_weight
            + self.pressure_weight
        )

        if total_weight <= 0.0:
            carrying_capacity_index = 0.0
        else:
            carrying_capacity_index = (
                self.resource_weight * resource_availability
                + self.regeneration_weight * regeneration_rate
                + self.pressure_weight * (1.0 - population_pressure)
            ) / total_weight

        carrying_capacity_index = self._clamp(
            carrying_capacity_index
        )

        status = (
            "sustainable"
            if carrying_capacity_index >= 0.7
            else "overshoot"
        )

        return {
            "resource_availability": resource_availability,
            "regeneration_rate": regeneration_rate,
            "population_pressure": population_pressure,
            "carrying_capacity_index": carrying_capacity_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "resource_weight": self.resource_weight,
                "regeneration_weight": self.regeneration_weight,
                "pressure_weight": self.pressure_weight,
                "status": status,
            },
        }

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.evaluate(inputs)

    def validate(
        self,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        result = self.evaluate(inputs)
        index = result["carrying_capacity_index"]
        return {
            "is_valid": 0.0 <= index <= 1.0,
            "carrying_capacity_index": index,
            "diagnostics": result["diagnostics"],
        }
