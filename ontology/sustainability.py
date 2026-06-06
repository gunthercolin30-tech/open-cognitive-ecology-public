PRIMITIVE = "sustainability"
DESCRIPTION = "Sustainability."
DEPENDENCIES = []


"""
SUSTAINABILITY
==============

This primitive formalizes sustainability as the long-term compatibility between
ecological balance, regenerative processes, and systemic viability.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "SUSTAINABILITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class Sustainability:
    """Quantifies sustainability as a bounded index in [0, 1]."""

    def __init__(
        self,
        balance_weight: float = 1.0,
        regeneration_weight: float = 1.0,
        viability_weight: float = 1.0,
    ) -> None:
        self.balance_weight = max(0.0, float(balance_weight))
        self.regeneration_weight = max(0.0, float(regeneration_weight))
        self.viability_weight = max(0.0, float(viability_weight))

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

        ecological_balance = self._clamp(
            inputs.get("ecological_balance", 0.0)
        )
        resource_regeneration = self._clamp(
            inputs.get("resource_regeneration", 0.0)
        )
        long_term_viability = self._clamp(
            inputs.get("long_term_viability", 0.0)
        )

        total_weight = (
            self.balance_weight
            + self.regeneration_weight
            + self.viability_weight
        )

        if total_weight <= 0.0:
            sustainability_index = 0.0
        else:
            sustainability_index = (
                self.balance_weight * ecological_balance
                + self.regeneration_weight * resource_regeneration
                + self.viability_weight * long_term_viability
            ) / total_weight

        sustainability_index = self._clamp(sustainability_index)

        status = (
            "sustainable"
            if sustainability_index >= 0.7
            else "unsustainable"
        )

        return {
            "ecological_balance": ecological_balance,
            "resource_regeneration": resource_regeneration,
            "long_term_viability": long_term_viability,
            "sustainability_index": sustainability_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "balance_weight": self.balance_weight,
                "regeneration_weight": self.regeneration_weight,
                "viability_weight": self.viability_weight,
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
        index = result["sustainability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "sustainability_index": index,
            "diagnostics": result["diagnostics"],
        }
