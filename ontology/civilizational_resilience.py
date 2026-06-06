PRIMITIVE = "civilizational_resilience"
DESCRIPTION = "Civilizational resilience."
DEPENDENCIES = []

"""
CIVILIZATIONAL_RESILIENCE primitive.

Scientific formalization of the capacity of a civilization-scale system to
absorb disruptions, preserve critical functions, and restore continuity.

The primitive quantifies:
- shock_absorption
- functional_preservation
- recovery_capacity
- civilizational_resilience_index

All numerical outputs are bounded in [0, 1].
"""

from typing import Any, Dict

PRIMITIVE_NAME = "CIVILIZATIONAL_RESILIENCE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class CivilizationalResilience:
    """Formalizes long-term resilience of civilization-scale systems."""

    def __init__(
        self,
        absorption_weight: float = 1.0,
        preservation_weight: float = 1.0,
        recovery_weight: float = 1.0,
    ) -> None:
        self.absorption_weight = max(0.0, float(absorption_weight))
        self.preservation_weight = max(0.0, float(preservation_weight))
        self.recovery_weight = max(0.0, float(recovery_weight))

    def evaluate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        state = state or {}

        redundancy_level = _clamp(float(state.get("redundancy_level", 0.0)))
        institutional_stability = _clamp(
            float(state.get("institutional_stability", 0.0))
        )
        restoration_speed = _clamp(float(state.get("restoration_speed", 0.0)))
        adaptive_capacity = _clamp(float(state.get("adaptive_capacity", 0.0)))

        shock_absorption = redundancy_level
        functional_preservation = institutional_stability
        recovery_capacity = _clamp(
            0.5 * restoration_speed + 0.5 * adaptive_capacity
        )

        weighted_sum = (
            self.absorption_weight * shock_absorption
            + self.preservation_weight * functional_preservation
            + self.recovery_weight * recovery_capacity
        )
        total_weight = (
            self.absorption_weight
            + self.preservation_weight
            + self.recovery_weight
        )

        if total_weight <= 0.0:
            civilizational_resilience_index = 0.0
        else:
            civilizational_resilience_index = _clamp(
                weighted_sum / total_weight
            )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "absorption_weight": self.absorption_weight,
            "preservation_weight": self.preservation_weight,
            "recovery_weight": self.recovery_weight,
            "status": (
                "civilizational_resilience_present"
                if civilizational_resilience_index > 0.0
                else "civilizational_resilience_absent"
            ),
        }

        return {
            "shock_absorption": shock_absorption,
            "functional_preservation": functional_preservation,
            "recovery_capacity": recovery_capacity,
            "civilizational_resilience_index": civilizational_resilience_index,
            "diagnostics": diagnostics,
        }

    def step(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        return self.evaluate(state)

    def validate(self, state: Dict[str, Any] = None) -> Dict[str, Any]:
        result = self.evaluate(state)
        value = result["civilizational_resilience_index"]
        return {
            "is_valid": value >= 0.5,
            "value": value,
            "diagnostics": result["diagnostics"],
        }
