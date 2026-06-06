"""
EXPERIENCE_INTEGRATION_LOOP
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class ExperienceIntegrationLoop:
    primitive_name = "EXPERIENCE_INTEGRATION_LOOP"

    def __init__(self) -> None:
        self.memory = []

    def step(
        self,
        objective: str = "",
        action_result: Optional[Dict[str, Any]] = None,
        expected_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        action_result = action_result or {}
        expected_result = expected_result or {}

        objective_score = float(expected_result.get("success_score", 1.0))
        achieved_score = float(action_result.get("success_score", 0.0))
        gap = objective_score - achieved_score

        learning_points: List[str] = []
        if gap <= 0:
            learning_points.append("Outcome meets or exceeds expectations.")
            strategy_adjustment = "reinforce_current_strategy"
        else:
            learning_points.append(
                f"Performance gap detected: {gap:.3f}. Strategy should be adjusted."
            )
            strategy_adjustment = "adjust_strategy"

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "objective": objective,
            "expected_result": expected_result,
            "action_result": action_result,
            "performance_gap": gap,
            "learning_points": learning_points,
            "strategy_adjustment": strategy_adjustment,
        }

        self.memory.append(record)

        return {
            "primitive": self.primitive_name,
            "integrated": True,
            "memory_updated": True,
            "performance_gap": gap,
            "learning_points": learning_points,
            "strategy_adjustment": strategy_adjustment,
            "experience_records": len(self.memory),
            "state": record,
        }


__all__ = ["ExperienceIntegrationLoop"]
