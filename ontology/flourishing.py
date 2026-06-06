PRIMITIVE = "flourishing"
DESCRIPTION = "Flourishing."
DEPENDENCIES = []

"""
FLOURISHING
===========

This primitive formalizes flourishing as the positive realization of a system's
potential under conditions of sustained viability, adaptive capacity, and
systemic harmony.

The flourishing index integrates three bounded components:

- well_being: degree of realized positive functioning.
- capability_realization: extent to which latent capacities are actualized.
- systemic_harmony: compatibility between internal and external constraints.

This primitive captures the transition from mere persistence to enduring
positive development.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "FLOURISHING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class Flourishing:
    """Quantifies flourishing as a bounded index in [0, 1]."""

    def __init__(
        self,
        well_being_weight: float = 1.0,
        capability_weight: float = 1.0,
        harmony_weight: float = 1.0,
    ) -> None:
        self.well_being_weight = max(0.0, float(well_being_weight))
        self.capability_weight = max(0.0, float(capability_weight))
        self.harmony_weight = max(0.0, float(harmony_weight))

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

        well_being = self._clamp(inputs.get("well_being", 0.0))
        capability_realization = self._clamp(
            inputs.get("capability_realization", 0.0)
        )
        systemic_harmony = self._clamp(
            inputs.get("systemic_harmony", 0.0)
        )

        total_weight = (
            self.well_being_weight
            + self.capability_weight
            + self.harmony_weight
        )

        if total_weight <= 0.0:
            flourishing_index = 0.0
        else:
            flourishing_index = (
                self.well_being_weight * well_being
                + self.capability_weight * capability_realization
                + self.harmony_weight * systemic_harmony
            ) / total_weight

        flourishing_index = self._clamp(flourishing_index)

        status = (
            "flourishing"
            if flourishing_index >= 0.7
            else "constrained"
        )

        return {
            "well_being": well_being,
            "capability_realization": capability_realization,
            "systemic_harmony": systemic_harmony,
            "flourishing_index": flourishing_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "well_being_weight": self.well_being_weight,
                "capability_weight": self.capability_weight,
                "harmony_weight": self.harmony_weight,
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
        index = result["flourishing_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "flourishing_index": index,
            "diagnostics": result["diagnostics"],
        }
