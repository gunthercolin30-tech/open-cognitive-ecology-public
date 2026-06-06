PRIMITIVE = "technological_amplification"
DESCRIPTION = "Technological amplification."
DEPENDENCIES = []

"""
TECHNOLOGICAL_AMPLIFICATION primitive.

Scientific formalization of the extension of cognitive capacities through
external technical artifacts, tools, and infrastructures.

The primitive quantifies:
- tool_integration
- capability_extension
- performance_scaling
- technological_amplification_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "TECHNOLOGICAL_AMPLIFICATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class TechnologicalAmplification:
    """
    Formalizes the amplification of cognitive capacities through technology.
    """

    def __init__(
        self,
        integration_weight: float = 1.0,
        extension_weight: float = 1.0,
        scaling_weight: float = 1.0,
    ) -> None:
        self.integration_weight = max(0.0, float(integration_weight))
        self.extension_weight = max(0.0, float(extension_weight))
        self.scaling_weight = max(0.0, float(scaling_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - interface_fluency
        - automation_support
        - capability_gain
        - throughput_multiplier
        """
        state = state or {}

        interface_fluency = _clamp(float(state.get("interface_fluency", 0.0)))
        automation_support = _clamp(float(state.get("automation_support", 0.0)))
        capability_gain = _clamp(float(state.get("capability_gain", 0.0)))
        throughput_multiplier = _clamp(
            float(state.get("throughput_multiplier", 0.0))
        )

        tool_integration = _clamp(
            0.5 * interface_fluency + 0.5 * automation_support
        )
        capability_extension = capability_gain
        performance_scaling = throughput_multiplier

        weighted_sum = (
            self.integration_weight * tool_integration
            + self.extension_weight * capability_extension
            + self.scaling_weight * performance_scaling
        )
        total_weight = (
            self.integration_weight
            + self.extension_weight
            + self.scaling_weight
        )

        if total_weight <= 0.0:
            technological_amplification_index = 0.0
        else:
            technological_amplification_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "integration_weight": self.integration_weight,
            "extension_weight": self.extension_weight,
            "scaling_weight": self.scaling_weight,
            "status": (
                "technological_amplification_present"
                if technological_amplification_index > 0.0
                else "technological_amplification_absent"
            ),
        }

        return {
            "tool_integration": tool_integration,
            "capability_extension": capability_extension,
            "performance_scaling": performance_scaling,
            "technological_amplification_index": (
                technological_amplification_index
            ),
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether technological amplification is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["technological_amplification_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
