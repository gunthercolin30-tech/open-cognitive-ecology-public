from ontology.longitudinal_civilizational_autonomy_tracker import (
    LongitudinalCivilizationalAutonomyTracker,
)

"""
WORLD_MODEL_EXECUTION_LOOP

Closes the loop between world modeling, prediction, planning, execution,
and feedback-driven model updating.
"""

from typing import Dict, Any


class WorldModelExecutionLoop:
    """Computes closed-loop autonomy quality metrics."""

    def __init__(self):
        self.tracker = LongitudinalCivilizationalAutonomyTracker()

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        world_model_coherence = self._clip(inputs.get("world_model_coherence", 0.5))
        predictive_simulation_index = self._clip(
            inputs.get("predictive_simulation_index", 0.5)
        )
        embodied_planning_index = self._clip(
            inputs.get("embodied_planning_index", 0.5)
        )
        execution_success = self._clip(inputs.get("execution_success", 0.5))
        feedback_integration = self._clip(inputs.get("feedback_integration", 0.5))
        adaptive_learning = self._clip(inputs.get("adaptive_learning", 0.5))

        closed_loop_autonomy_index = self._clip(
            0.15 * world_model_coherence
            + 0.15 * predictive_simulation_index
            + 0.20 * embodied_planning_index
            + 0.20 * execution_success
            + 0.15 * feedback_integration
            + 0.15 * adaptive_learning
        )

        if closed_loop_autonomy_index >= 0.95:
            loop_class = "canonical_closed_loop_autonomy"
        elif closed_loop_autonomy_index >= 0.85:
            loop_class = "high_fidelity_closed_loop_autonomy"
        elif closed_loop_autonomy_index >= 0.70:
            loop_class = "functional_closed_loop_autonomy"
        else:
            loop_class = "partial_closed_loop_autonomy"

        longitudinal = self.tracker.step(closed_loop_autonomy_index)

        return {
            "closed_loop_autonomy_index": round(closed_loop_autonomy_index, 4),
            "world_model_execution_score": round(closed_loop_autonomy_index, 4),
            "loop_class": loop_class,
            "longitudinal_trend": longitudinal.get("trend"),
            "autonomy_history_length": longitudinal.get("history_length"),
        }

