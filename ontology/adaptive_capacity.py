PRIMITIVE = "adaptive_capacity"
DESCRIPTION = "Adaptive capacity."
DEPENDENCIES = []

"""
ADAPTIVE_CAPACITY
=================

This primitive formalizes adaptive capacity as the integrated ability of a
system to reorganize in response to perturbations while preserving viability.

The adaptive capacity index integrates three bounded components:

- learning_capacity: ability to extract information from experience.
- reconfiguration_flexibility: ability to modify structures and strategies.
- resource_mobilization: ability to redirect resources toward adaptation.

This primitive synthesizes the operational potential for viable transformation
under changing constraints.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "ADAPTIVE_CAPACITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class AdaptiveCapacity:
    """Quantifies adaptive capacity as a bounded index in [0, 1]."""

    def __init__(
        self,
        learning_weight: float = 1.0,
        flexibility_weight: float = 1.0,
        mobilization_weight: float = 1.0,
    ) -> None:
        self.learning_weight = max(0.0, float(learning_weight))
        self.flexibility_weight = max(0.0, float(flexibility_weight))
        self.mobilization_weight = max(0.0, float(mobilization_weight))

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

        learning_capacity = self._clamp(
            inputs.get("learning_capacity", 0.0)
        )
        reconfiguration_flexibility = self._clamp(
            inputs.get("reconfiguration_flexibility", 0.0)
        )
        resource_mobilization = self._clamp(
            inputs.get("resource_mobilization", 0.0)
        )

        total_weight = (
            self.learning_weight
            + self.flexibility_weight
            + self.mobilization_weight
        )

        if total_weight <= 0.0:
            adaptive_capacity_index = 0.0
        else:
            adaptive_capacity_index = (
                self.learning_weight * learning_capacity
                + self.flexibility_weight * reconfiguration_flexibility
                + self.mobilization_weight * resource_mobilization
            ) / total_weight

        adaptive_capacity_index = self._clamp(adaptive_capacity_index)

        status = (
            "adaptive"
            if adaptive_capacity_index >= 0.7
            else "rigid"
        )

        return {
            "learning_capacity": learning_capacity,
            "reconfiguration_flexibility": reconfiguration_flexibility,
            "resource_mobilization": resource_mobilization,
            "adaptive_capacity_index": adaptive_capacity_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "learning_weight": self.learning_weight,
                "flexibility_weight": self.flexibility_weight,
                "mobilization_weight": self.mobilization_weight,
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
        index = result["adaptive_capacity_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "adaptive_capacity_index": index,
            "diagnostics": result["diagnostics"],
        }
