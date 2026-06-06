"""
Civilizational Intelligence Growth Index.
Synthesizes consciousness, autonomy, knowledge, and viability.
"""

from __future__ import annotations

PRIMITIVE = "CIVILIZATIONAL_INTELLIGENCE_GROWTH_INDEX"

DEPENDENCIES = [
    "civilizational_knowledge_accumulation_index",
    "civilizational_autonomy_index",
    "global_viability_score",
]


class CivilizationalIntelligenceGrowthIndex:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        unified_consciousness_score: float = 0.917,
        civilizational_autonomy_score: float = 0.9367,
        civilizational_knowledge_score: float = 1.0,
        global_viability_score: float = 0.92457,
    ) -> dict:
        u = self._clamp(unified_consciousness_score)
        a = self._clamp(civilizational_autonomy_score)
        k = self._clamp(civilizational_knowledge_score)
        g = self._clamp(global_viability_score)

        score = (u + a + k + g) / 4.0

        if score >= 0.95:
            certification = "Civilizational Intelligence Growth Gold"
        elif score >= 0.90:
            certification = "Advanced Civilizational Intelligence"
        elif score >= 0.75:
            certification = "Developing Civilizational Intelligence"
        else:
            certification = "Early Civilizational Intelligence"

        return {
            "primitive": self.primitive,
            "civilizational_intelligence_growth_score": score,
            "certification": certification,
            "diagnostics": {
                "unified_consciousness_score": u,
                "civilizational_autonomy_score": a,
                "civilizational_knowledge_score": k,
                "global_viability_score": g,
            },
        }
