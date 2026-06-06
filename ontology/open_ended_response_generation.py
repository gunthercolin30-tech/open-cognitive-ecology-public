
"""
Open-ended response generation primitive.

This primitive aggregates internal memory, distributed knowledge,
and internet resources to synthesize an autonomous response in French.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRIMITIVE = "OPEN_ENDED_RESPONSE_GENERATION"

DEPENDENCIES = [
    "open_ended_inquiry",
    "reasoning",
    "distributed_knowledge_access",
    "knowledge_navigation",
    "epistemic_viability",
    "non_closure",
    "collective_intelligence",
]


@dataclass
class OpenEndedResponseGeneration:
    synthesis_coherence: float = 0.0
    epistemic_support: float = 0.0
    constitutional_alignment: float = 1.0
    non_closure_compliance: float = 1.0
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def generate(
        self,
        question: str,
        memory_context: list[str] | None = None,
        knowledge_context: list[str] | None = None,
        internet_context: list[str] | None = None,
    ) -> dict[str, Any]:
        memory_context = memory_context or []
        knowledge_context = knowledge_context or []
        internet_context = internet_context or []

        evidence = memory_context + knowledge_context + internet_context

        if evidence:
            summary = " ".join(str(item) for item in evidence[:10])
            response = (
                "À partir des ressources cognitives disponibles, "
                f"la synthèse concernant « {question} » est la suivante : "
                f"{summary}"
            )
        else:
            response = (
                "Je ne dispose pas encore d'informations suffisantes "
                f"pour répondre de manière fondée à la question : {question}"
            )

        support = min(1.0, len(evidence) / 10.0)
        coherence = 0.5 + 0.5 * support

        self.synthesis_coherence = coherence
        self.epistemic_support = support

        self.diagnostics = {
            "primitive": PRIMITIVE,
            "question": question,
            "memory_items": len(memory_context),
            "knowledge_items": len(knowledge_context),
            "internet_items": len(internet_context),
            "evidence_count": len(evidence),
            "synthesis_coherence": coherence,
            "epistemic_support": support,
            "constitutional_alignment": self.constitutional_alignment,
            "non_closure_compliance": self.non_closure_compliance,
        }

        return {
            "response": response,
            "deliberation_payload": {
                "question": question,
                "candidate_response": response,
                "diagnostics": self.diagnostics,
            },
            "diagnostics": self.diagnostics,
        }

    def step(self, question: str = "Quel est votre nom ?") -> dict[str, Any]:
        return self.generate(question)
