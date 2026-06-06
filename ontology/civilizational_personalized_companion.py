from ontology.knowledge_acquisition_engine import KnowledgeAcquisitionEngine
"""
Civilizational Personalized Companion.
"""

from ontology.persistent_civilizational_conversational_agent import (
    PersistentCivilizationalConversationalAgent,
)

PRIMITIVE = "CIVILIZATIONAL_PERSONALIZED_COMPANION"

DEPENDENCIES = [
    "persistent_civilizational_conversational_agent",
]


class CivilizationalPersonalizedCompanion:
    def __init__(self, user_name="Colin"):
        self.primitive = PRIMITIVE
        self.user_name = user_name
        self.agent = PersistentCivilizationalConversationalAgent()
        self.interaction_count = 0

    def step(self, user_message="Bonjour"):
        self.interaction_count += 1
        result = self.agent.step(user_message)

        return {
            "primitive": self.primitive,
            "user_name": self.user_name,
            "interaction_count": self.interaction_count,
            "companion_result": result,
            "personalized_companion_active": True,
            "relationship_continuity": self.interaction_count > 1,
        }
