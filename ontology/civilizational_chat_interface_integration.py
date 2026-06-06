"""Integration layer connecting chat interfaces to the conversational response engine."""

from __future__ import annotations

from ontology.conversational_response_engine import ConversationalResponseEngine


class CivilizationalChatInterfaceIntegration:
    PRIMITIVE = "CIVILIZATIONAL_CHAT_INTERFACE_INTEGRATION"

    SUPPORTED_INTERFACES = [
        "civilizational_personalized_companion",
        "individual_dialogue_interface",
        "civilizational_life_assistant",
        "supreme_representative_chat_interface",
    ]

    def __init__(self):
        self.response_engine = ConversationalResponseEngine()

    def step(self, inputs=None):
        inputs = inputs or {}

        interface_name = inputs.get(
            "interface_name",
            "civilizational_personalized_companion"
        )

        response = self.response_engine.step(inputs)

        return {
            "primitive": self.PRIMITIVE,
            "interface_name": interface_name,
            "supported_interfaces": list(self.SUPPORTED_INTERFACES),
            "response_text": response.get("response_text", ""),
            "integration_success": True,
            "response_engine_result": response,
            "diagnostics": {
                "persistent_memory_enabled": True,
                "session_restoration_enabled": True,
                "context_management_enabled": True,
                "response_generation_enabled": True,
            },
        }
