PRIMITIVE = "knowledge_accumulation"
DESCRIPTION = "Knowledge accumulation."
DEPENDENCIES = []

"""
KNOWLEDGE_ACCUMULATION primitive.

Scientific formalization of the cumulative aggregation and retention of
knowledge over time within collective cognitive systems.

The primitive quantifies:
- knowledge_growth
- retention_efficiency
- integration_capacity
- knowledge_accumulation_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "KNOWLEDGE_ACCUMULATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class KnowledgeAccumulation:
    """Formalizes cumulative growth of collective knowledge."""

    def __init__(
        self,
        growth_weight: float = 1.0,
        retention_weight: float = 1.0,
        integration_weight: float = 1.0,
    ) -> None:
        self.growth_weight = max(0.0, float(growth_weight))
        self.retention_weight = max(0.0, float(retention_weight))
        self.integration_weight = max(0.0, float(integration_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        state = state or {}

        discovery_rate = _clamp(float(state.get("discovery_rate", 0.0)))
        preservation_quality = _clamp(
            float(state.get("preservation_quality", 0.0))
        )
        synthesis_capacity = _clamp(
            float(state.get("synthesis_capacity", 0.0))
        )
        interoperability = _clamp(
            float(state.get("interoperability", 0.0))
        )

        knowledge_growth = discovery_rate
        retention_efficiency = preservation_quality
        integration_capacity = _clamp(
            0.5 * synthesis_capacity + 0.5 * interoperability
        )

        weighted_sum = (
            self.growth_weight * knowledge_growth
            + self.retention_weight * retention_efficiency
            + self.integration_weight * integration_capacity
        )
        total_weight = (
            self.growth_weight
            + self.retention_weight
            + self.integration_weight
        )

        if total_weight <= 0.0:
            knowledge_accumulation_index = 0.0
        else:
            knowledge_accumulation_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "growth_weight": self.growth_weight,
            "retention_weight": self.retention_weight,
            "integration_weight": self.integration_weight,
            "status": (
                "knowledge_accumulation_present"
                if knowledge_accumulation_index > 0.0
                else "knowledge_accumulation_absent"
            ),
        }

        return {
            "knowledge_growth": knowledge_growth,
            "retention_efficiency": retention_efficiency,
            "integration_capacity": integration_capacity,
            "knowledge_accumulation_index": knowledge_accumulation_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        result = self.evaluate(state)
        value = result["knowledge_accumulation_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
