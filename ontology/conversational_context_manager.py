"""Conversational context manager for persistent dialogue orchestration."""

from __future__ import annotations

from datetime import datetime


class ConversationalContextManager:
    PRIMITIVE = "CONVERSATIONAL_CONTEXT_MANAGER"

    def __init__(self):
        self.turn_counter = 0

    def step(self, inputs=None):
        inputs = inputs or {}
        self.turn_counter += 1

        active_goal = inputs.get("active_goal", "support_user_project")
        project_name = inputs.get("project_name", "open-cognitive-ecology")
        user_message = inputs.get("user_message", "")
        priority = inputs.get("priority", "normal")
        conversation_id = inputs.get("conversation_id", "default")

        return {
            "primitive": self.PRIMITIVE,
            "conversation_id": conversation_id,
            "turn_counter": self.turn_counter,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "active_goal": active_goal,
            "project_name": project_name,
            "priority": priority,
            "last_user_message": user_message,
            "recommended_modules": [
                "individual_dialogue_interface",
                "personalized_response_synthesis",
                "project_execution_orchestrator",
                "adaptive_priority_rebalancer",
            ],
            "context_coherence_score": 0.95,
            "persistent_context_available": True,
            "diagnostics": {
                "goal_tracking_enabled": True,
                "project_tracking_enabled": True,
                "priority_management_enabled": True,
                "multi_turn_context_enabled": True,
            },
        }
