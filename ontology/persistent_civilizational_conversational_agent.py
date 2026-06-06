"""
Persistent Civilizational Conversational Agent.
"""

from ontology.civilizational_conversational_agent import CivilizationalConversationalAgent
from ontology.civilizational_dialogue_memory import CivilizationalDialogueMemory

PRIMITIVE = "PERSISTENT_CIVILIZATIONAL_CONVERSATIONAL_AGENT"

DEPENDENCIES = [
    "civilizational_conversational_agent",
    "civilizational_dialogue_memory",
]


class PersistentCivilizationalConversationalAgent:
    def __init__(self):
        self.primitive = PRIMITIVE
        self.agent = CivilizationalConversationalAgent()
        self.memory = CivilizationalDialogueMemory()

    def step(self, user_message="Bonjour"):
        response = self.agent.step(user_message)
        memory_result = self.memory.step(
            user_message=user_message,
            agent_response=response.get("response", ""),
        )

        return {
            "primitive": self.primitive,
            "user_message": user_message,
            "agent_result": response,
            "memory_result": memory_result,
            "persistent_dialogue_active": True,
        }
