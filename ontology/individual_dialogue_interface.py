"""
Individual Dialogue Interface.

Provides a persistent conversational interface for an individual
artificial agent. Maintains dialogue history and exposes a simple
functional interaction layer without any claim of phenomenological
subjectivity.
"""

from __future__ import annotations
from ontology.knowledge_acquisition_engine import KnowledgeAcquisitionEngine

PRIMITIVE = "individual_dialogue_interface"

DEPENDENCIES = [
    "autobiographical_memory",
    "self_model",
    "introspective_reporting",
    "self_narrative_generation",
    "autonomous_world_exploration_engine",
]


class IndividualDialogueInterface:
    def __init__(self) -> None:
        self.dialogue_history = []

    def step(
        self,
        user_message: str = "",
        self_coherence: float = 0.0,
        autobiographical_relevance: float = 0.0,
        introspective_clarity: float = 0.0,
    ) -> dict:
        self.dialogue_history.append({
            "role": "user",
            "content": str(user_message),
        })

        dialogue_continuity = min(1.0, len(self.dialogue_history) / 100.0)

        dialogue_quality = (
            max(0.0, min(1.0, float(self_coherence))) +
            max(0.0, min(1.0, float(autobiographical_relevance))) +
            max(0.0, min(1.0, float(introspective_clarity)))
        ) / 3.0

        individual_dialogue_interface_index = (
            dialogue_continuity + dialogue_quality
        ) / 2.0

        response = (
            "Message received and integrated into the individual's "
            "ongoing autobiographical dialogue."
        )

        self.dialogue_history.append({
            "role": "assistant",
            "content": response,
        })

        return {
            "primitive": PRIMITIVE.upper(),
            "dialogue_turns": len(self.dialogue_history),
            "dialogue_continuity": dialogue_continuity,
            "dialogue_quality": dialogue_quality,
            "individual_dialogue_interface_index":
                individual_dialogue_interface_index,
            "response": response,
            "diagnostics": {
                "history_length": len(self.dialogue_history),
                "dependencies": DEPENDENCIES,
            },
        }
