"""Proactive Assistance Workflows."""

from __future__ import annotations

from typing import Any, Dict, List

from ontology.long_term_personalized_planning import LongTermPersonalizedPlanning
from ontology.civilizational_strategy_orchestrator import CivilizationalStrategyOrchestrator


class ProactiveAssistanceWorkflows:
    PRIMITIVE = "PROACTIVE_ASSISTANCE_WORKFLOWS"

    def __init__(self, user_name: str = "User") -> None:
        self.user_name = user_name
        self.planning = LongTermPersonalizedPlanning(user_name=user_name)
        self.strategy = CivilizationalStrategyOrchestrator()

    def _generate_recommendations(self, objective: Dict[str, Any] | None) -> List[str]:
        if not objective:
            return [
                "Define a high-priority scientific or personal objective.",
                "Break the objective into milestones.",
                "Schedule the next concrete action.",
            ]

        text = objective.get("objective", "")
        return [
            f"Clarify the scope of: {text}",
            "Define three measurable milestones.",
            "Identify the next concrete action to perform today.",
            "Prepare supporting references and resources.",
        ]

    def step(self, message: str = "") -> Dict[str, Any]:
        if message:
            self.planning.step(message)

        plan_state = self.planning.step()
        latest = plan_state.get("latest_objective")
        recommendations = self._generate_recommendations(latest)

        try:
            strategy_state = self.strategy.step()
        except Exception:
            strategy_state = {}

        return {
            "primitive": self.PRIMITIVE,
            "user_name": self.user_name,
            "objective_count": plan_state.get("objective_count", 0),
            "latest_objective": latest,
            "recommendations": recommendations,
            "strategy_state": strategy_state,
            "workflow_active": True,
        }


def step(message: str = "", user_name: str = "User") -> Dict[str, Any]:
    return ProactiveAssistanceWorkflows(user_name=user_name).step(message)
