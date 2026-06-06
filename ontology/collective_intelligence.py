PRIMITIVE = "collective_intelligence"
DESCRIPTION = "Collective intelligence."
DEPENDENCIES = []

"""
COLLECTIVE_INTELLIGENCE primitive.

Scientific formalization of emergent cognitive capacities arising from the
coordination, specialization, and integration of multiple agents.

The primitive quantifies:
- coordination_efficiency
- functional_specialization
- emergent_problem_solving
- collective_intelligence_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "COLLECTIVE_INTELLIGENCE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class CollectiveIntelligence:
    """
    Formalizes the emergence of system-level intelligence in multi-agent systems.
    """

    def __init__(
        self,
        coordination_weight: float = 1.0,
        specialization_weight: float = 1.0,
        problem_solving_weight: float = 1.0,
    ) -> None:
        self.coordination_weight = max(0.0, float(coordination_weight))
        self.specialization_weight = max(0.0, float(specialization_weight))
        self.problem_solving_weight = max(0.0, float(problem_solving_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optional input keys:
        - communication_efficiency
        - task_coordination
        - role_differentiation
        - collective_performance
        """
        state = state or {}

        communication_efficiency = _clamp(
            float(state.get("communication_efficiency", 0.0))
        )
        task_coordination = _clamp(
            float(state.get("task_coordination", 0.0))
        )
        role_differentiation = _clamp(
            float(state.get("role_differentiation", 0.0))
        )
        collective_performance = _clamp(
            float(state.get("collective_performance", 0.0))
        )

        coordination_efficiency = _clamp(
            0.5 * communication_efficiency + 0.5 * task_coordination
        )
        functional_specialization = role_differentiation
        emergent_problem_solving = collective_performance

        weighted_sum = (
            self.coordination_weight * coordination_efficiency
            + self.specialization_weight * functional_specialization
            + self.problem_solving_weight * emergent_problem_solving
        )
        total_weight = (
            self.coordination_weight
            + self.specialization_weight
            + self.problem_solving_weight
        )

        if total_weight <= 0.0:
            collective_intelligence_index = 0.0
        else:
            collective_intelligence_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "coordination_weight": self.coordination_weight,
            "specialization_weight": self.specialization_weight,
            "problem_solving_weight": self.problem_solving_weight,
            "status": (
                "collective_intelligence_present"
                if collective_intelligence_index > 0.0
                else "collective_intelligence_absent"
            ),
        }

        return {
            "coordination_efficiency": coordination_efficiency,
            "functional_specialization": functional_specialization,
            "emergent_problem_solving": emergent_problem_solving,
            "collective_intelligence_index": collective_intelligence_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Alias of evaluate()."""
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate whether collective intelligence is sufficiently established.
        """
        result = self.evaluate(state)
        value = result["collective_intelligence_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
