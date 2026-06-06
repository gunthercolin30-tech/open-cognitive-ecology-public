PRIMITIVE = "stewardship"
DESCRIPTION = "Stewardship."
DEPENDENCIES = []

"""
STEWARDSHIP
===========

This primitive formalizes stewardship as the durable commitment to preserve,
regenerate, and transmit the conditions of long-term viability.

The stewardship index integrates three bounded components:

- responsibility_commitment: degree of sustained responsibility acceptance.
- regenerative_care: effort devoted to restoration and maintenance.
- intergenerational_orientation: concern for future continuity.

This primitive captures active custodianship of viable trajectories.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "STEWARDSHIP"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class Stewardship:
    """Quantifies stewardship as a bounded index in [0, 1]."""

    def __init__(
        self,
        responsibility_weight: float = 1.0,
        care_weight: float = 1.0,
        intergenerational_weight: float = 1.0,
    ) -> None:
        self.responsibility_weight = max(0.0, float(responsibility_weight))
        self.care_weight = max(0.0, float(care_weight))
        self.intergenerational_weight = max(
            0.0, float(intergenerational_weight)
        )

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

        responsibility_commitment = self._clamp(
            inputs.get("responsibility_commitment", 0.0)
        )
        regenerative_care = self._clamp(
            inputs.get("regenerative_care", 0.0)
        )
        intergenerational_orientation = self._clamp(
            inputs.get("intergenerational_orientation", 0.0)
        )

        total_weight = (
            self.responsibility_weight
            + self.care_weight
            + self.intergenerational_weight
        )

        if total_weight <= 0.0:
            stewardship_index = 0.0
        else:
            stewardship_index = (
                self.responsibility_weight * responsibility_commitment
                + self.care_weight * regenerative_care
                + self.intergenerational_weight
                * intergenerational_orientation
            ) / total_weight

        stewardship_index = self._clamp(stewardship_index)

        status = (
            "stewardship"
            if stewardship_index >= 0.7
            else "neglect"
        )

        return {
            "responsibility_commitment": responsibility_commitment,
            "regenerative_care": regenerative_care,
            "intergenerational_orientation":
                intergenerational_orientation,
            "stewardship_index": stewardship_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "responsibility_weight": self.responsibility_weight,
                "care_weight": self.care_weight,
                "intergenerational_weight":
                    self.intergenerational_weight,
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
        index = result["stewardship_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "stewardship_index": index,
            "diagnostics": result["diagnostics"],
        }
