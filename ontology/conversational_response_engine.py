"""Generate conversational responses from the autonomous dialogue pipeline."""

from __future__ import annotations

from ontology.autonomous_dialogue_orchestrator import AutonomousDialogueOrchestrator


class ConversationalResponseEngine:
    PRIMITIVE = "CONVERSATIONAL_RESPONSE_ENGINE"

    def __init__(self):
        self.orchestrator = AutonomousDialogueOrchestrator()

    def step(self, inputs=None):
        inputs = inputs or {}
        orchestration = self.orchestrator.step(inputs)

        user_message = inputs.get("user_message", "")
        updated_context = orchestration.get("updated_context", {})

        if user_message.strip():
            response_text = (
                "Contexte conversationnel mis à jour avec succès. "
                f"Dernier message utilisateur : {user_message}"
            )
        else:
            response_text = (
                "Session restaurée et contexte conversationnel disponible."
            )

        return {
            "primitive": self.PRIMITIVE,
            "response_text": response_text,
            "orchestration": orchestration,
            "response_generation_success": True,
            "active_goal": updated_context.get("active_goal"),
            "project_name": updated_context.get("project_name"),
            "diagnostics": {
                "contextual_response_generation": True,
                "persistent_memory_used": True,
            },
        }
