"""
AUTONOMOUS_SCIENTIFIC_DIRECTOR

Coordinates autonomous experimentation, analysis, meta-analysis,
publication, and scientific prioritization.
"""

from typing import Dict, Any


class AutonomousScientificDirector:
    """Computes autonomous scientific governance metrics."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        experimentation_quality = self._clip(
            inputs.get("experimentation_quality", 0.5)
        )
        statistical_rigor = self._clip(inputs.get("statistical_rigor", 0.5))
        meta_analysis_strength = self._clip(
            inputs.get("meta_analysis_strength", 0.5)
        )
        publication_readiness = self._clip(
            inputs.get("publication_readiness", 0.5)
        )
        prioritization_quality = self._clip(
            inputs.get("prioritization_quality", 0.5)
        )
        theoretical_coherence = self._clip(
            inputs.get("theoretical_coherence", 0.5)
        )

        autonomous_scientific_director_index = self._clip(
            0.20 * experimentation_quality
            + 0.15 * statistical_rigor
            + 0.15 * meta_analysis_strength
            + 0.15 * publication_readiness
            + 0.15 * prioritization_quality
            + 0.20 * theoretical_coherence
        )

        if autonomous_scientific_director_index >= 0.95:
            director_class = "canonical_autonomous_scientific_director"
        elif autonomous_scientific_director_index >= 0.85:
            director_class = "high_fidelity_autonomous_scientific_director"
        elif autonomous_scientific_director_index >= 0.70:
            director_class = "functional_autonomous_scientific_director"
        else:
            director_class = "partial_autonomous_scientific_director"

        return {
            "autonomous_scientific_director_index": round(
                autonomous_scientific_director_index, 4
            ),
            "scientific_autonomy_score": round(
                autonomous_scientific_director_index, 4
            ),
            "director_class": director_class,
        }
