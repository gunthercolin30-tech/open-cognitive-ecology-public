"""
LIFE_HISTORY_SYNTHESIS_ENGINE

Synthesizes major life events into a coherent autobiographical narrative
structure and computes indicators of narrative continuity.
"""

from typing import Dict, Any


class LifeHistorySynthesisEngine:
    """Builds a structured life-history synthesis."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        event_count = max(0.0, float(inputs.get("event_count", 0.0)))
        chronological_coherence = self._clip(inputs.get("chronological_coherence", 0.5))
        identity_relevance = self._clip(inputs.get("identity_relevance", 0.5))
        project_integration = self._clip(inputs.get("project_integration", 0.5))
        publication_integration = self._clip(inputs.get("publication_integration", 0.5))
        future_alignment = self._clip(inputs.get("future_alignment", 0.5))

        coverage_score = self._clip(event_count / 50.0)

        narrative_continuity_score = self._clip(
            0.25 * chronological_coherence
            + 0.20 * identity_relevance
            + 0.20 * project_integration
            + 0.15 * publication_integration
            + 0.20 * future_alignment
        )

        synthesis_quality_index = self._clip(
            0.40 * coverage_score + 0.60 * narrative_continuity_score
        )

        if synthesis_quality_index >= 0.95:
            synthesis_class = "canonical_life_history"
        elif synthesis_quality_index >= 0.85:
            synthesis_class = "high_fidelity_life_history"
        elif synthesis_quality_index >= 0.70:
            synthesis_class = "coherent_life_history"
        else:
            synthesis_class = "partial_life_history"

        return {
            "coverage_score": round(coverage_score, 4),
            "narrative_continuity_score": round(narrative_continuity_score, 4),
            "life_history_synthesis_index": round(synthesis_quality_index, 4),
            "timeline_density": round(event_count, 2),
            "synthesis_class": synthesis_class,
        }
