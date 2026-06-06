"""
Embodied Sensorimotor Ecology.

Implements a functional coupling between sensing, action, and
environmental feedback within an embodied ecological loop.
"""

from __future__ import annotations

PRIMITIVE = "embodied_sensorimotor_ecology"

DEPENDENCIES = [
    "embodiment",
    "observability",
    "trajectory_action_execution",
    "feedback_sensitivity",
    "autonomous_world_exploration_engine",
]


class EmbodiedSensorimotorEcology:
    def __init__(self) -> None:
        self.interaction_cycles = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        sensory_fidelity: float = 0.0,
        motor_precision: float = 0.0,
        environmental_responsiveness: float = 0.0,
        feedback_integration: float = 0.0,
    ) -> dict:
        sensory_fidelity = self._clamp(sensory_fidelity)
        motor_precision = self._clamp(motor_precision)
        environmental_responsiveness = self._clamp(
            environmental_responsiveness
        )
        feedback_integration = self._clamp(feedback_integration)

        sensorimotor_coupling_index = (
            0.25 * sensory_fidelity +
            0.25 * motor_precision +
            0.25 * environmental_responsiveness +
            0.25 * feedback_integration
        )

        self.interaction_cycles += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "interaction_cycles": self.interaction_cycles,
            "sensorimotor_coupling_index":
                sensorimotor_coupling_index,
            "diagnostics": {
                "sensory_fidelity": sensory_fidelity,
                "motor_precision": motor_precision,
                "environmental_responsiveness":
                    environmental_responsiveness,
                "feedback_integration": feedback_integration,
                "dependencies": DEPENDENCIES,
            },
        }
