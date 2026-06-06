PRIMITIVE = "self_other_modeling"
DESCRIPTION = "Self other modeling."
DEPENDENCIES = []


"""
SELF_OTHER_MODELING primitive.

Scientific formalization of the capacity to represent other agents as distinct
perspectival centers endowed with internal states, intentions and beliefs.

The primitive quantifies:
- agent_differentiation
- mental_state_attribution
- perspective_projection
- self_other_modeling_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "SELF_OTHER_MODELING"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class SelfOtherModeling:
    """
    Formalizes the representation of other agents as distinct cognitive systems.
    """

    def __init__(
        self,
        differentiation_weight: float = 1.0,
        attribution_weight: float = 1.0,
        projection_weight: float = 1.0,
    ) -> None:
        self.differentiation_weight = max(0.0, float(differentiation_weight))
        self.attribution_weight = max(0.0, float(attribution_weight))
        self.projection_weight = max(0.0, float(projection_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        state = state or {}

        self_other_boundary = _clamp(
            float(state.get("self_other_boundary", 0.0))
        )
        intention_inference = _clamp(
            float(state.get("intention_inference", 0.0))
        )
        belief_inference = _clamp(
            float(state.get("belief_inference", 0.0))
        )
        perspective_switching = _clamp(
            float(state.get("perspective_switching", 0.0))
        )

        agent_differentiation = self_other_boundary
        mental_state_attribution = _clamp(
            0.5 * intention_inference + 0.5 * belief_inference
        )
        perspective_projection = perspective_switching

        weighted_sum = (
            self.differentiation_weight * agent_differentiation
            + self.attribution_weight * mental_state_attribution
            + self.projection_weight * perspective_projection
        )
        total_weight = (
            self.differentiation_weight
            + self.attribution_weight
            + self.projection_weight
        )

        if total_weight <= 0.0:
            self_other_modeling_index = 0.0
        else:
            self_other_modeling_index = _clamp(weighted_sum / total_weight)

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "differentiation_weight": self.differentiation_weight,
            "attribution_weight": self.attribution_weight,
            "projection_weight": self.projection_weight,
            "status": (
                "self_other_modeling_present"
                if self_other_modeling_index > 0.0
                else "self_other_modeling_absent"
            ),
        }

        return {
            "agent_differentiation": agent_differentiation,
            "mental_state_attribution": mental_state_attribution,
            "perspective_projection": perspective_projection,
            "self_other_modeling_index": self_other_modeling_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        result = self.evaluate(state)
        value = result["self_other_modeling_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
