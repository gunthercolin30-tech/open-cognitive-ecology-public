PRIMITIVE = "ecological_footprint"
DESCRIPTION = "Ecological footprint."
DEPENDENCIES = []

"""
ECOLOGICAL_FOOTPRINT
====================

This primitive formalizes ecological footprint as the relative pressure exerted
by a system on ecological resources and regenerative capacities.

The ecological footprint index integrates three bounded components:

- resource_consumption: intensity of material and energy use.
- waste_generation: intensity of residual outputs and pollution.
- biocapacity_ratio: ratio between available biocapacity and demand.

High resource consumption and waste increase ecological pressure, while high
biocapacity_ratio reduces effective footprint.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "ECOLOGICAL_FOOTPRINT"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class EcologicalFootprint:
    """Quantifies ecological footprint as a bounded pressure index in [0, 1]."""

    def __init__(
        self,
        consumption_weight: float = 1.0,
        waste_weight: float = 1.0,
        biocapacity_weight: float = 1.0,
    ) -> None:
        self.consumption_weight = max(0.0, float(consumption_weight))
        self.waste_weight = max(0.0, float(waste_weight))
        self.biocapacity_weight = max(0.0, float(biocapacity_weight))

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

        resource_consumption = self._clamp(
            inputs.get("resource_consumption", 0.0)
        )
        waste_generation = self._clamp(
            inputs.get("waste_generation", 0.0)
        )
        biocapacity_ratio = self._clamp(
            inputs.get("biocapacity_ratio", 0.0)
        )

        total_weight = (
            self.consumption_weight
            + self.waste_weight
            + self.biocapacity_weight
        )

        if total_weight <= 0.0:
            ecological_footprint_index = 0.0
        else:
            ecological_footprint_index = (
                self.consumption_weight * resource_consumption
                + self.waste_weight * waste_generation
                + self.biocapacity_weight * (1.0 - biocapacity_ratio)
            ) / total_weight

        ecological_footprint_index = self._clamp(
            ecological_footprint_index
        )

        status = (
            "overshoot"
            if ecological_footprint_index >= 0.7
            else "sustainable"
        )

        return {
            "resource_consumption": resource_consumption,
            "waste_generation": waste_generation,
            "biocapacity_ratio": biocapacity_ratio,
            "ecological_footprint_index": ecological_footprint_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "consumption_weight": self.consumption_weight,
                "waste_weight": self.waste_weight,
                "biocapacity_weight": self.biocapacity_weight,
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
        index = result["ecological_footprint_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "ecological_footprint_index": index,
            "diagnostics": result["diagnostics"],
        }
