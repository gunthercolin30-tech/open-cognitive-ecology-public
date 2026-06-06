"""
LONGITUDINAL_RELATIONSHIP_EVOLUTION_ANALYZER

Analyzes temporal trends in relationship continuity metrics.
"""

from typing import Dict, Any


class LongitudinalRelationshipEvolutionAnalyzer:
    """Computes longitudinal trend indicators for a relationship."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        current_index = self._clip(inputs.get("current_index", 0.5))
        previous_index = self._clip(inputs.get("previous_index", 0.5))
        stability = self._clip(inputs.get("stability", 0.5))
        engagement_growth = self._clip(inputs.get("engagement_growth", 0.5))
        memory_enrichment = self._clip(inputs.get("memory_enrichment", 0.5))
        trust_growth = self._clip(inputs.get("trust_growth", 0.5))

        delta = current_index - previous_index
        normalized_delta = self._clip((delta + 1.0) / 2.0)

        longitudinal_growth_index = self._clip(
            0.30 * normalized_delta
            + 0.20 * stability
            + 0.15 * engagement_growth
            + 0.15 * memory_enrichment
            + 0.20 * trust_growth
        )

        if delta >= 0.02:
            trend_class = "strengthening"
        elif delta <= -0.02:
            trend_class = "weakening"
        else:
            trend_class = "stable"

        if longitudinal_growth_index >= 0.95:
            evolutionary_phase = "canonical_enduring_bond"
        elif longitudinal_growth_index >= 0.85:
            evolutionary_phase = "deepening_enduring_bond"
        elif longitudinal_growth_index >= 0.70:
            evolutionary_phase = "developing_bond"
        else:
            evolutionary_phase = "fragile_bond"

        return {
            "relationship_delta": round(delta, 4),
            "normalized_delta": round(normalized_delta, 4),
            "longitudinal_growth_index": round(longitudinal_growth_index, 4),
            "trend_class": trend_class,
            "evolutionary_phase": evolutionary_phase,
        }
