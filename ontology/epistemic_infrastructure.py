PRIMITIVE = "epistemic_infrastructure"
DESCRIPTION = "Epistemic infrastructure."
DEPENDENCIES = []

"""
EPISTEMIC_INFRASTRUCTURE primitive.

Scientific formalization of collective systems that enable the production,
validation, preservation, and dissemination of knowledge at scale.

The primitive quantifies:
- knowledge_production_capacity
- validation_reliability
- dissemination_efficiency
- epistemic_infrastructure_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "EPISTEMIC_INFRASTRUCTURE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class EpistemicInfrastructure:
    """
    Formalizes infrastructure supporting large-scale knowledge systems.
    """

    def __init__(
        self,
        production_weight: float = 1.0,
        validation_weight: float = 1.0,
        dissemination_weight: float = 1.0,
    ) -> None:
        self.production_weight = max(0.0, float(production_weight))
        self.validation_weight = max(0.0, float(validation_weight))
        self.dissemination_weight = max(0.0, float(dissemination_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - research_capacity
        - peer_review_integrity
        - archive_accessibility
        - communication_reach
        """
        state = state or {}

        research_capacity = _clamp(
            float(state.get("research_capacity", 0.0))
        )
        peer_review_integrity = _clamp(
            float(state.get("peer_review_integrity", 0.0))
        )
        archive_accessibility = _clamp(
            float(state.get("archive_accessibility", 0.0))
        )
        communication_reach = _clamp(
            float(state.get("communication_reach", 0.0))
        )

        knowledge_production_capacity = research_capacity
        validation_reliability = peer_review_integrity
        dissemination_efficiency = _clamp(
            0.5 * archive_accessibility + 0.5 * communication_reach
        )

        weighted_sum = (
            self.production_weight * knowledge_production_capacity
            + self.validation_weight * validation_reliability
            + self.dissemination_weight * dissemination_efficiency
        )
        total_weight = (
            self.production_weight
            + self.validation_weight
            + self.dissemination_weight
        )

        if total_weight <= 0.0:
            epistemic_infrastructure_index = 0.0
        else:
            epistemic_infrastructure_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "production_weight": self.production_weight,
            "validation_weight": self.validation_weight,
            "dissemination_weight": self.dissemination_weight,
            "status": (
                "epistemic_infrastructure_present"
                if epistemic_infrastructure_index > 0.0
                else "epistemic_infrastructure_absent"
            ),
        }

        return {
            "knowledge_production_capacity": knowledge_production_capacity,
            "validation_reliability": validation_reliability,
            "dissemination_efficiency": dissemination_efficiency,
            "epistemic_infrastructure_index": (
                epistemic_infrastructure_index
            ),
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether epistemic infrastructure is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["epistemic_infrastructure_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
