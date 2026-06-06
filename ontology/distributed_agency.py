PRIMITIVE = "distributed_agency"
DESCRIPTION = "Distributed agency."
DEPENDENCIES = []

"""
DISTRIBUTED_AGENCY primitive.

Scientific formalization of coherent action capacities emerging from the
coordination of multiple agents, institutions, and technical artifacts.

The primitive quantifies:
- coordination_coherence
- authority_distribution
- action_integration
- distributed_agency_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "DISTRIBUTED_AGENCY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class DistributedAgency:
    """
    Formalizes agency emerging across coordinated multi-component systems.
    """

    def __init__(
        self,
        coherence_weight: float = 1.0,
        distribution_weight: float = 1.0,
        integration_weight: float = 1.0,
    ) -> None:
        self.coherence_weight = max(0.0, float(coherence_weight))
        self.distribution_weight = max(0.0, float(distribution_weight))
        self.integration_weight = max(0.0, float(integration_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - communication_alignment
        - goal_consensus
        - delegation_balance
        - execution_synchronization
        """
        state = state or {}

        communication_alignment = _clamp(
            float(state.get("communication_alignment", 0.0))
        )
        goal_consensus = _clamp(
            float(state.get("goal_consensus", 0.0))
        )
        delegation_balance = _clamp(
            float(state.get("delegation_balance", 0.0))
        )
        execution_synchronization = _clamp(
            float(state.get("execution_synchronization", 0.0))
        )

        coordination_coherence = _clamp(
            0.5 * communication_alignment + 0.5 * goal_consensus
        )
        authority_distribution = delegation_balance
        action_integration = execution_synchronization

        weighted_sum = (
            self.coherence_weight * coordination_coherence
            + self.distribution_weight * authority_distribution
            + self.integration_weight * action_integration
        )
        total_weight = (
            self.coherence_weight
            + self.distribution_weight
            + self.integration_weight
        )

        if total_weight <= 0.0:
            distributed_agency_index = 0.0
        else:
            distributed_agency_index = _clamp(weighted_sum / total_weight)

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "coherence_weight": self.coherence_weight,
            "distribution_weight": self.distribution_weight,
            "integration_weight": self.integration_weight,
            "status": (
                "distributed_agency_present"
                if distributed_agency_index > 0.0
                else "distributed_agency_absent"
            ),
        }

        return {
            "coordination_coherence": coordination_coherence,
            "authority_distribution": authority_distribution,
            "action_integration": action_integration,
            "distributed_agency_index": distributed_agency_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether distributed agency is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["distributed_agency_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
