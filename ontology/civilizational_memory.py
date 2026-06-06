PRIMITIVE = "civilizational_memory"
DESCRIPTION = "Civilizational memory."
DEPENDENCIES = []

"""
CIVILIZATIONAL_MEMORY primitive.

Scientific formalization of the long-term preservation and intergenerational
transmission of knowledge, norms, and symbolic structures beyond individual
agents.

The primitive quantifies:
- knowledge_preservation
- intergenerational_transmission
- archive_stability
- civilizational_memory_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "CIVILIZATIONAL_MEMORY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class CivilizationalMemory:
    """
    Formalizes the preservation of knowledge across generations.
    """

    def __init__(
        self,
        preservation_weight: float = 1.0,
        transmission_weight: float = 1.0,
        archive_weight: float = 1.0,
    ) -> None:
        self.preservation_weight = max(0.0, float(preservation_weight))
        self.transmission_weight = max(0.0, float(transmission_weight))
        self.archive_weight = max(0.0, float(archive_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - knowledge_retention
        - educational_fidelity
        - cultural_reproduction
        - archival_integrity
        """
        state = state or {}

        knowledge_retention = _clamp(
            float(state.get("knowledge_retention", 0.0))
        )
        educational_fidelity = _clamp(
            float(state.get("educational_fidelity", 0.0))
        )
        cultural_reproduction = _clamp(
            float(state.get("cultural_reproduction", 0.0))
        )
        archival_integrity = _clamp(
            float(state.get("archival_integrity", 0.0))
        )

        knowledge_preservation = knowledge_retention

        intergenerational_transmission = _clamp(
            0.5 * educational_fidelity + 0.5 * cultural_reproduction
        )

        archive_stability = archival_integrity

        weighted_sum = (
            self.preservation_weight * knowledge_preservation
            + self.transmission_weight * intergenerational_transmission
            + self.archive_weight * archive_stability
        )
        total_weight = (
            self.preservation_weight
            + self.transmission_weight
            + self.archive_weight
        )

        if total_weight <= 0.0:
            civilizational_memory_index = 0.0
        else:
            civilizational_memory_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "preservation_weight": self.preservation_weight,
            "transmission_weight": self.transmission_weight,
            "archive_weight": self.archive_weight,
            "status": (
                "civilizational_memory_present"
                if civilizational_memory_index > 0.0
                else "civilizational_memory_absent"
            ),
        }

        return {
            "knowledge_preservation": knowledge_preservation,
            "intergenerational_transmission": (
                intergenerational_transmission
            ),
            "archive_stability": archive_stability,
            "civilizational_memory_index": civilizational_memory_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether civilizational memory is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["civilizational_memory_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
