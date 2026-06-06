"""Autonomous orchestration of the persistent dialogue pipeline."""

from __future__ import annotations

from ontology.conversational_context_manager import ConversationalContextManager
from ontology.dialogue_memory_persistence import DialogueMemoryPersistence
from ontology.conversational_session_restorer import ConversationalSessionRestorer


class AutonomousDialogueOrchestrator:
    PRIMITIVE = "AUTONOMOUS_DIALOGUE_ORCHESTRATOR"

    def __init__(self):
        self.restorer = ConversationalSessionRestorer()
        self.context_manager = ConversationalContextManager()
        self.persistence = DialogueMemoryPersistence()

    def step(self, inputs=None):
        inputs = inputs or {}

        restoration = self.restorer.step()

        context_inputs = {
            "conversation_id": inputs.get("conversation_id", "default"),
            "user_message": inputs.get("user_message", ""),
            "active_goal": inputs.get(
                "active_goal",
                restoration.get("active_goal") or "support_user_project"
            ),
            "project_name": inputs.get(
                "project_name",
                restoration.get("project_name") or "open-cognitive-ecology"
            ),
            "priority": inputs.get("priority", "normal"),
        }

        updated_context = self.context_manager.step(context_inputs)
        save_result = self.persistence.step({
            "context_state": updated_context
        })

        return {
            "primitive": self.PRIMITIVE,
            "restoration": restoration,
            "updated_context": updated_context,
            "save_result": save_result,
            "dialogue_orchestration_success": (
                restoration.get("restoration_success", False)
                and save_result.get("success", False)
            ),
            "diagnostics": {
                "automatic_restoration": True,
                "context_update": True,
                "persistent_save": True,
            },
        }
