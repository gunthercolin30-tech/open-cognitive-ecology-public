PRIMITIVE = "long_term_coordination"
DESCRIPTION = "Long term coordination."
DEPENDENCIES = []

"""
LONG_TERM_COORDINATION primitive.

Scientific formalization of the capacity of collective systems to synchronize
actions and commitments over extended temporal horizons.

The primitive quantifies:
- commitment_stability
- intergenerational_alignment
- planning_continuity
- long_term_coordination_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "LONG_TERM_COORDINATION"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class LongTermCoordination:
    """Formalizes coordination sustained across long temporal scales."""

    def __init__(
        self,
        commitment_weight: float = 1.0,
        alignment_weight: float = 1.0,
        continuity_weight: float = 1.0,
    ) -> None:
        self.commitment_weight = max(0.0, float(commitment_weight))
        self.alignment_weight = max(0.0, float(alignment_weight))
        self.continuity_weight = max(0.0, float(continuity_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        state = state or {}

        agreement_durability = _clamp(
            float(state.get("agreement_durability", 0.0))
        )
        succession_fidelity = _clamp(
            float(state.get("succession_fidelity", 0.0))
        )
        strategic_consistency = _clamp(
            float(state.get("strategic_consistency", 0.0))
        )
        institutional_follow_through = _clamp(
            float(state.get("institutional_follow_through", 0.0))
        )

        commitment_stability = agreement_durability
        intergenerational_alignment = succession_fidelity
        planning_continuity = _clamp(
            0.5 * strategic_consistency
            + 0.5 * institutional_follow_through
        )

        weighted_sum = (
            self.commitment_weight * commitment_stability
            + self.alignment_weight * intergenerational_alignment
            + self.continuity_weight * planning_continuity
        )
        total_weight = (
            self.commitment_weight
            + self.alignment_weight
            + self.continuity_weight
        )

        if total_weight <= 0.0:
            long_term_coordination_index = 0.0
        else:
            long_term_coordination_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "commitment_weight": self.commitment_weight,
            "alignment_weight": self.alignment_weight,
            "continuity_weight": self.continuity_weight,
            "status": (
                "long_term_coordination_present"
                if long_term_coordination_index > 0.0
                else "long_term_coordination_absent"
            ),
        }

        return {
            "commitment_stability": commitment_stability,
            "intergenerational_alignment": intergenerational_alignment,
            "planning_continuity": planning_continuity,
            "long_term_coordination_index": long_term_coordination_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        result = self.evaluate(state)
        value = result["long_term_coordination_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
