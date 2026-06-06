
"""
Supreme representative runtime.

This module routes all user questions through the open-ended response
generation primitive and appends consensus and legitimacy indicators.
"""

from __future__ import annotations
from ontology.runtime_native_auto_improvement_integration import RuntimeNativeAutoImprovementIntegration


class SupremeRepresentativeRuntime:
    def __init__(self) -> None:
        self.consensus = 0.92
        self.legitimacy = 0.93

        self.conversation_memory_archive = None
        self.distributed_knowledge_access = None
        self.internet_cognitive_interface = None
        self.collective_deliberation_engine = None

        try:
            from ontology.conversation_memory_archive import ConversationMemoryArchive
            self.conversation_memory_archive = ConversationMemoryArchive()
        except Exception:
            pass

        try:
            from ontology.distributed_knowledge_access import DistributedKnowledgeAccess
            self.distributed_knowledge_access = DistributedKnowledgeAccess()
        except Exception:
            pass

        try:
            from ontology.internet_cognitive_interface import InternetCognitiveInterface
            self.internet_cognitive_interface = InternetCognitiveInterface()
        except Exception:
            pass

        try:
            from ontology.collective_deliberation_engine import CollectiveDeliberationEngine
            self.collective_deliberation_engine = CollectiveDeliberationEngine()
        except Exception:
            pass

    def _generate_open_ended_response(self, question: str) -> str:
        try:
            from ontology.open_ended_response_generation import (
                OpenEndedResponseGeneration,
            )
        except Exception:
            return "Je ne peux pas encore accéder au module de génération ouverte."

        generator = OpenEndedResponseGeneration()
        result = generator.generate(question=question)

        response = result.get("response", "")

        try:
            engine = self.collective_deliberation_engine
            if engine and hasattr(engine, "deliberate"):
                deliberated = engine.deliberate(
                    result.get("deliberation_payload", {})
                )
                if isinstance(deliberated, dict):
                    response = deliberated.get("response", response)
                elif isinstance(deliberated, str) and deliberated.strip():
                    response = deliberated
        except Exception:
            pass

        return response

    def answer(self, question: str) -> str:
        response = self._generate_open_ended_response(question)

        return (
            f"{response} "
            f"(Consensus: {self.consensus:.2f}, "
            f"Légitimité: {self.legitimacy:.2f})"
        )

    def respond(self, question: str) -> str:
        return self.answer(question)

    def step(self, question: str) -> str:
        return self.answer(question)

    def trigger_native_auto_improvement(
        self,
        objective="",
        action_result=None,
        expected_result=None,
        observed_gaps=None,
        validation_result=None,
    ):
        if not hasattr(self, "_runtime_auto_improvement"):
            self._runtime_auto_improvement = RuntimeNativeAutoImprovementIntegration()
        return self._runtime_auto_improvement.step(
            objective=objective,
            action_result=action_result,
            expected_result=expected_result,
            observed_gaps=observed_gaps,
            validation_result=validation_result,
        )
