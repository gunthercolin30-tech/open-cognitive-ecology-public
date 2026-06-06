
"""
Civilizational Autonomy Index
Aggregates civilization-scale capabilities into a single autonomy score.
"""

from __future__ import annotations

PRIMITIVE = "CIVILIZATIONAL_AUTONOMY_INDEX"

DEPENDENCIES = [
    "civilizational_memory",
    "self_narrative_generation",
    "governance",
    "epistemic_infrastructure",
    "distributed_agency",
    "long_term_coordination",
    "autonomy",
    "constitutional_integrity_index",
    "non_closure",
]


class CivilizationalAutonomyIndex:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _certification(score: float) -> str:
        if score < 0.40:
            return "Emerging"
        if score < 0.60:
            return "Developing"
        if score < 0.75:
            return "Advanced"
        if score < 0.90:
            return "Highly Autonomous"
        return "Civilizational Autonomy Gold"

    def step(
        self,
        civilizational_memory: float = 0.0,
        narrative_identity: float = 0.0,
        governance: float = 0.0,
        epistemic_infrastructure: float = 0.0,
        distributed_agency: float = 0.0,
        long_term_coordination: float = 0.0,
        autonomy: float = 0.0,
        constitutional_integrity: float = 0.0,
        non_closure: float = 0.0,
    ) -> dict:
        components = {
            "civilizational_memory": self._clamp(civilizational_memory),
            "narrative_identity": self._clamp(narrative_identity),
            "governance": self._clamp(governance),
            "epistemic_infrastructure": self._clamp(epistemic_infrastructure),
            "distributed_agency": self._clamp(distributed_agency),
            "long_term_coordination": self._clamp(long_term_coordination),
            "autonomy": self._clamp(autonomy),
            "constitutional_integrity": self._clamp(constitutional_integrity),
            "non_closure": self._clamp(non_closure),
        }

        score = sum(components.values()) / len(components)
        score = self._clamp(score)

        certification = self._certification(score)

        return {
            "primitive": self.primitive,
            "civilizational_autonomy_score": score,
            "certification": certification,
            "constitutionally_aligned": components["constitutional_integrity"] >= 0.75,
            "non_closure_compliant": components["non_closure"] >= 0.75,
            "diagnostics": components,
        }
