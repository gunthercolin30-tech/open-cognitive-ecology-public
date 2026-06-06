"""Automatic restoration of the latest conversational context."""

from __future__ import annotations

from ontology.dialogue_memory_persistence import DialogueMemoryPersistence


class ConversationalSessionRestorer:
    PRIMITIVE = "CONVERSATIONAL_SESSION_RESTORER"

    def __init__(self):
        self.persistence = DialogueMemoryPersistence()

    def step(self, inputs=None):
        load_result = self.persistence.step({"action": "load"})
        context_state = load_result.get("context_state", {})

        return {
            "primitive": self.PRIMITIVE,
            "restoration_success": load_result.get("success", False),
            "restored_context": context_state,
            "active_goal": context_state.get("active_goal"),
            "project_name": context_state.get("project_name"),
            "restored_fields": sorted(context_state.keys()),
            "diagnostics": {
                "automatic_restoration_enabled": True,
                "context_available": bool(context_state),
            },
        }
