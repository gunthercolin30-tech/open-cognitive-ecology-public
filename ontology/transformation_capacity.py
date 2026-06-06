PRIMITIVE = "transformation_capacity"
DESCRIPTION = "Transformation capacity."
DEPENDENCIES = []

"""
TRANSFORMATION_CAPACITY
=======================

This primitive formalizes transformation capacity as the integrated ability of a
system to reconfigure structures, institutions, and goals when incremental
adaptation is insufficient to maintain viability.

The transformation capacity index integrates three bounded components:

- structural_reconfiguration: ability to redesign system architecture.
- institutional_innovation: ability to create new coordination rules.
- goal_redefinition: ability to revise objectives and value structures.

This primitive captures regime-shift potential under changing constraints.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "TRANSFORMATION_CAPACITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class TransformationCapacity:
    """Quantifies transformation capacity as a bounded index in [0, 1]."""

    def __init__(
        self,
        structural_weight: float = 1.0,
        institutional_weight: float = 1.0,
        goal_weight: float = 1.0,
    ) -> None:
        self.structural_weight = max(0.0, float(structural_weight))
        self.institutional_weight = max(0.0, float(institutional_weight))
        self.goal_weight = max(0.0, float(goal_weight))

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

        structural_reconfiguration = self._clamp(
            inputs.get("structural_reconfiguration", 0.0)
        )
        institutional_innovation = self._clamp(
            inputs.get("institutional_innovation", 0.0)
        )
        goal_redefinition = self._clamp(
            inputs.get("goal_redefinition", 0.0)
        )

        total_weight = (
            self.structural_weight
            + self.institutional_weight
            + self.goal_weight
        )

        if total_weight <= 0.0:
            transformation_capacity_index = 0.0
        else:
            transformation_capacity_index = (
                self.structural_weight * structural_reconfiguration
                + self.institutional_weight * institutional_innovation
                + self.goal_weight * goal_redefinition
            ) / total_weight

        transformation_capacity_index = self._clamp(
            transformation_capacity_index
        )

        status = (
            "transformative"
            if transformation_capacity_index >= 0.7
            else "path_dependent"
        )

        return {
            "structural_reconfiguration": structural_reconfiguration,
            "institutional_innovation": institutional_innovation,
            "goal_redefinition": goal_redefinition,
            "transformation_capacity_index": transformation_capacity_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "structural_weight": self.structural_weight,
                "institutional_weight": self.institutional_weight,
                "goal_weight": self.goal_weight,
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
        index = result["transformation_capacity_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "transformation_capacity_index": index,
            "diagnostics": result["diagnostics"],
        }
