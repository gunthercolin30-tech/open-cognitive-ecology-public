PRIMITIVE = "cultural_evolution"
DESCRIPTION = "Cultural evolution."
DEPENDENCIES = []

"""
CULTURAL_EVOLUTION primitive.

Scientific formalization of the transmission, variation and selective retention
of symbolic or behavioral structures across populations.

The primitive quantifies:
- transmission_fidelity
- cultural_variation
- selective_retention
- cultural_evolution_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "CULTURAL_EVOLUTION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class CulturalEvolution:
    """
    Formalizes cumulative cultural dynamics.
    """

    def __init__(
        self,
        transmission_weight: float = 1.0,
        variation_weight: float = 1.0,
        retention_weight: float = 1.0,
    ) -> None:
        self.transmission_weight = max(0.0, float(transmission_weight))
        self.variation_weight = max(0.0, float(variation_weight))
        self.retention_weight = max(0.0, float(retention_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - imitation_accuracy
        - innovation_rate
        - adaptive_selection
        - memory_persistence
        """
        state = state or {}

        imitation_accuracy = _clamp(
            float(state.get("imitation_accuracy", 0.0))
        )
        innovation_rate = _clamp(
            float(state.get("innovation_rate", 0.0))
        )
        adaptive_selection = _clamp(
            float(state.get("adaptive_selection", 0.0))
        )
        memory_persistence = _clamp(
            float(state.get("memory_persistence", 0.0))
        )

        transmission_fidelity = imitation_accuracy
        cultural_variation = innovation_rate
        selective_retention = _clamp(
            0.5 * adaptive_selection + 0.5 * memory_persistence
        )

        weighted_sum = (
            self.transmission_weight * transmission_fidelity
            + self.variation_weight * cultural_variation
            + self.retention_weight * selective_retention
        )
        total_weight = (
            self.transmission_weight
            + self.variation_weight
            + self.retention_weight
        )

        if total_weight <= 0.0:
            cultural_evolution_index = 0.0
        else:
            cultural_evolution_index = _clamp(weighted_sum / total_weight)

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "transmission_weight": self.transmission_weight,
            "variation_weight": self.variation_weight,
            "retention_weight": self.retention_weight,
            "status": (
                "cultural_evolution_present"
                if cultural_evolution_index > 0.0
                else "cultural_evolution_absent"
            ),
        }

        return {
            "transmission_fidelity": transmission_fidelity,
            "cultural_variation": cultural_variation,
            "selective_retention": selective_retention,
            "cultural_evolution_index": cultural_evolution_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether cumulative cultural evolution is established.
        """
        result = self.evaluate(state)
        value = result["cultural_evolution_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
