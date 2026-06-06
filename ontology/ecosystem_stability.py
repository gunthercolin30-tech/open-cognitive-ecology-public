PRIMITIVE = "ecosystem_stability"
DESCRIPTION = "Ecosystem stability."
DEPENDENCIES = []

"""
ECOSYSTEM_STABILITY
===================

This primitive formalizes ecosystem stability as the capacity of an ecological
system to maintain essential functions, resist perturbations, and recover after
disturbances.

The ecosystem stability index integrates three bounded components:

- functional_integrity: preservation of ecological functions.
- disturbance_resistance: ability to absorb perturbations.
- recovery_capacity: capacity to restore viable functioning.

The primitive is foundational because stable ecosystems provide the ecological
substrate upon which biodiversity preservation, regenerative capacity, and
civilizational viability depend.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "ECOSYSTEM_STABILITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class EcosystemStability:
    """Quantifies ecosystem stability as a bounded index in [0, 1]."""

    def __init__(
        self,
        functional_weight: float = 1.0,
        resistance_weight: float = 1.0,
        recovery_weight: float = 1.0,
    ) -> None:
        self.functional_weight = max(0.0, float(functional_weight))
        self.resistance_weight = max(0.0, float(resistance_weight))
        self.recovery_weight = max(0.0, float(recovery_weight))

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

        functional_integrity = self._clamp(
            inputs.get("functional_integrity", 0.0)
        )
        disturbance_resistance = self._clamp(
            inputs.get("disturbance_resistance", 0.0)
        )
        recovery_capacity = self._clamp(
            inputs.get("recovery_capacity", 0.0)
        )

        total_weight = (
            self.functional_weight
            + self.resistance_weight
            + self.recovery_weight
        )

        if total_weight <= 0.0:
            ecosystem_stability_index = 0.0
        else:
            ecosystem_stability_index = (
                self.functional_weight * functional_integrity
                + self.resistance_weight * disturbance_resistance
                + self.recovery_weight * recovery_capacity
            ) / total_weight

        ecosystem_stability_index = self._clamp(
            ecosystem_stability_index
        )

        status = (
            "stable"
            if ecosystem_stability_index >= 0.7
            else "unstable"
        )

        return {
            "functional_integrity": functional_integrity,
            "disturbance_resistance": disturbance_resistance,
            "recovery_capacity": recovery_capacity,
            "ecosystem_stability_index": ecosystem_stability_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "functional_weight": self.functional_weight,
                "resistance_weight": self.resistance_weight,
                "recovery_weight": self.recovery_weight,
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
        index = result["ecosystem_stability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "ecosystem_stability_index": index,
            "diagnostics": result["diagnostics"],
        }
