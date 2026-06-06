PRIMITIVE = "ecosystem_services"
DESCRIPTION = "Ecosystem services."
DEPENDENCIES = []

"""
ECOSYSTEM_SERVICES
==================

This primitive formalizes ecosystem services as the functional benefits
provided by ecological systems to biological and civilizational processes.

The ecosystem services index integrates three bounded components:

- provisioning_services: material resources supplied by ecosystems.
- regulating_services: climate, water, and stability regulation functions.
- supporting_services: underlying processes sustaining ecosystem function.

This primitive captures the mediation between ecological integrity and
long-term systemic viability.
"""

from typing import Any, Dict, Optional

PRIMITIVE_NAME = "ECOSYSTEM_SERVICES"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


class EcosystemServices:
    """Quantifies ecosystem services as a bounded index in [0, 1]."""

    def __init__(
        self,
        provisioning_weight: float = 1.0,
        regulating_weight: float = 1.0,
        supporting_weight: float = 1.0,
    ) -> None:
        self.provisioning_weight = max(0.0, float(provisioning_weight))
        self.regulating_weight = max(0.0, float(regulating_weight))
        self.supporting_weight = max(0.0, float(supporting_weight))

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

        provisioning_services = self._clamp(
            inputs.get("provisioning_services", 0.0)
        )
        regulating_services = self._clamp(
            inputs.get("regulating_services", 0.0)
        )
        supporting_services = self._clamp(
            inputs.get("supporting_services", 0.0)
        )

        total_weight = (
            self.provisioning_weight
            + self.regulating_weight
            + self.supporting_weight
        )

        if total_weight <= 0.0:
            ecosystem_services_index = 0.0
        else:
            ecosystem_services_index = (
                self.provisioning_weight * provisioning_services
                + self.regulating_weight * regulating_services
                + self.supporting_weight * supporting_services
            ) / total_weight

        ecosystem_services_index = self._clamp(
            ecosystem_services_index
        )

        status = (
            "sustained"
            if ecosystem_services_index >= 0.7
            else "degraded"
        )

        return {
            "provisioning_services": provisioning_services,
            "regulating_services": regulating_services,
            "supporting_services": supporting_services,
            "ecosystem_services_index": ecosystem_services_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "provisioning_weight": self.provisioning_weight,
                "regulating_weight": self.regulating_weight,
                "supporting_weight": self.supporting_weight,
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
        index = result["ecosystem_services_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "ecosystem_services_index": index,
            "diagnostics": result["diagnostics"],
        }
