"""
Cognitive Resource Economy.

Implements allocation, budgeting, and optimization of finite cognitive
resources such as attention, memory, and computational effort.
"""

from __future__ import annotations

PRIMITIVE = "cognitive_resource_economy"

DEPENDENCIES = [
    "attention_allocation",
    "resource_allocation",
    "execution",
    "prioritization",
    "monitoring",
]


class CognitiveResourceEconomy:
    def __init__(self) -> None:
        self.allocation_cycles = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        attention_budget: float = 0.0,
        memory_budget: float = 0.0,
        computation_budget: float = 0.0,
        allocation_efficiency: float = 0.0,
    ) -> dict:
        attention_budget = self._clamp(attention_budget)
        memory_budget = self._clamp(memory_budget)
        computation_budget = self._clamp(computation_budget)
        allocation_efficiency = self._clamp(allocation_efficiency)

        resource_utilization_index = (
            0.25 * attention_budget +
            0.25 * memory_budget +
            0.25 * computation_budget +
            0.25 * allocation_efficiency
        )

        self.allocation_cycles += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "allocation_cycles": self.allocation_cycles,
            "resource_utilization_index":
                resource_utilization_index,
            "diagnostics": {
                "attention_budget": attention_budget,
                "memory_budget": memory_budget,
                "computation_budget": computation_budget,
                "allocation_efficiency": allocation_efficiency,
                "dependencies": DEPENDENCIES,
            },
        }
