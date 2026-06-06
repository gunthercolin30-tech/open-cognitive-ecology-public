"""
Civilizational Knowledge Accumulation Index.
Quantifies cumulative scientific knowledge production.
"""

from __future__ import annotations

PRIMITIVE = "CIVILIZATIONAL_KNOWLEDGE_ACCUMULATION_INDEX"

DEPENDENCIES = [
    "autonomous_research_and_publication_loop",
    "civilizational_memory",
]


class CivilizationalKnowledgeAccumulationIndex:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        research_cycles: int = 10,
        hypotheses_generated: int = 30,
        publications_produced: int = 10,
        memory_integration_ratio: float = 1.0,
    ) -> dict:
        cycles_factor = min(1.0, research_cycles / 100.0)
        hypotheses_factor = min(1.0, hypotheses_generated / 300.0)
        publications_factor = min(1.0, publications_produced / 100.0)
        memory_factor = self._clamp(memory_integration_ratio)

        score = (
            cycles_factor
            + hypotheses_factor
            + publications_factor
            + memory_factor
        ) / 4.0

        if score >= 0.90:
            certification = "Civilizational Knowledge Gold"
        elif score >= 0.75:
            certification = "Advanced Knowledge Accumulation"
        elif score >= 0.50:
            certification = "Developing Knowledge Accumulation"
        else:
            certification = "Early Knowledge Accumulation"

        return {
            "primitive": self.primitive,
            "civilizational_knowledge_score": score,
            "certification": certification,
            "diagnostics": {
                "research_cycles": research_cycles,
                "hypotheses_generated": hypotheses_generated,
                "publications_produced": publications_produced,
                "memory_integration_ratio": memory_factor,
            },
        }
