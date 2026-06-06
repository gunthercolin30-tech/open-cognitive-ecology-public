"""
Narrative Identity Engine.

Implements dynamic construction and revision of autobiographical
narratives supporting persistent identity across time.
"""

from __future__ import annotations

PRIMITIVE = "narrative_identity_engine"

DEPENDENCIES = [
    "self_narrative_generation",
    "autobiographical_memory",
    "temporal_self_continuity",
    "individual_dialogue_interface",
    "developmental_growth_engine",
]


class NarrativeIdentityEngine:
    def __init__(self) -> None:
        self.revision_count = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        autobiographical_coherence: float = 0.0,
        temporal_continuity: float = 0.0,
        developmental_integration: float = 0.0,
        narrative_consistency: float = 0.0,
    ) -> dict:
        autobiographical_coherence = self._clamp(
            autobiographical_coherence
        )
        temporal_continuity = self._clamp(temporal_continuity)
        developmental_integration = self._clamp(
            developmental_integration
        )
        narrative_consistency = self._clamp(
            narrative_consistency
        )

        narrative_identity_index = (
            0.30 * autobiographical_coherence +
            0.25 * temporal_continuity +
            0.25 * developmental_integration +
            0.20 * narrative_consistency
        )

        self.revision_count += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "revision_count": self.revision_count,
            "narrative_identity_index":
                narrative_identity_index,
            "diagnostics": {
                "autobiographical_coherence":
                    autobiographical_coherence,
                "temporal_continuity": temporal_continuity,
                "developmental_integration":
                    developmental_integration,
                "narrative_consistency":
                    narrative_consistency,
                "dependencies": DEPENDENCIES,
            },
        }
