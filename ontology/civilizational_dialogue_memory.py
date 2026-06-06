
"""
Civilizational Dialogue Memory.
"""

from datetime import datetime

PRIMITIVE = "CIVILIZATIONAL_DIALOGUE_MEMORY"

DEPENDENCIES = [
    "civilizational_memory_archive",
    "conversation_memory_archive",
]


class CivilizationalDialogueMemory:
    def __init__(self):
        self.primitive = PRIMITIVE
        self.history = []

    def step(self, user_message="", agent_response=""):
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_message": user_message,
            "agent_response": agent_response,
        }
        self.history.append(record)

        return {
            "primitive": self.primitive,
            "dialogue_length": len(self.history),
            "latest_record": record,
            "continuity_established": len(self.history) > 1,
            "memory_active": True,
        }
