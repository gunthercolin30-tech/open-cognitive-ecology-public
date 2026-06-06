PRIMITIVE = "externalized_cognition"
DESCRIPTION = "Externalized cognition."
DEPENDENCIES = []

"""
EXTERNALIZED_COGNITION primitive.

Scientific formalization of the delegation of cognitive functions to external
supports such as documents, tools, databases, and artificial intelligence
systems.

The primitive quantifies:
- memory_offloading
- reasoning_delegation
- coordination_support
- externalized_cognition_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "EXTERNALIZED_COGNITION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class ExternalizedCognition:
    """
    Formalizes the transfer of cognitive functions to external artifacts.
    """

    def __init__(
        self,
        memory_weight: float = 1.0,
        reasoning_weight: float = 1.0,
        coordination_weight: float = 1.0,
    ) -> None:
        self.memory_weight = max(0.0, float(memory_weight))
        self.reasoning_weight = max(0.0, float(reasoning_weight))
        self.coordination_weight = max(0.0, float(coordination_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - storage_reliance
        - inference_assistance
        - workflow_support
        - collaboration_enablement
        """
        state = state or {}

        storage_reliance = _clamp(
            float(state.get("storage_reliance", 0.0))
        )
        inference_assistance = _clamp(
            float(state.get("inference_assistance", 0.0))
        )
        workflow_support = _clamp(
            float(state.get("workflow_support", 0.0))
        )
        collaboration_enablement = _clamp(
            float(state.get("collaboration_enablement", 0.0))
        )

        memory_offloading = storage_reliance
        reasoning_delegation = inference_assistance
        coordination_support = _clamp(
            0.5 * workflow_support + 0.5 * collaboration_enablement
        )

        weighted_sum = (
            self.memory_weight * memory_offloading
            + self.reasoning_weight * reasoning_delegation
            + self.coordination_weight * coordination_support
        )
        total_weight = (
            self.memory_weight
            + self.reasoning_weight
            + self.coordination_weight
        )

        if total_weight <= 0.0:
            externalized_cognition_index = 0.0
        else:
            externalized_cognition_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "memory_weight": self.memory_weight,
            "reasoning_weight": self.reasoning_weight,
            "coordination_weight": self.coordination_weight,
            "status": (
                "externalized_cognition_present"
                if externalized_cognition_index > 0.0
                else "externalized_cognition_absent"
            ),
        }

        return {
            "memory_offloading": memory_offloading,
            "reasoning_delegation": reasoning_delegation,
            "coordination_support": coordination_support,
            "externalized_cognition_index": externalized_cognition_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether externalized cognition is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["externalized_cognition_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
