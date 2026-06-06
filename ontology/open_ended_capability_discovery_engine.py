"""
OPEN_ENDED_CAPABILITY_DISCOVERY_ENGINE

Identifies high-value capabilities not yet implemented and prioritizes
the most promising ontology extensions.
"""

from typing import Dict, Any


class OpenEndedCapabilityDiscoveryEngine:
    """Computes open-ended capability discovery metrics."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        ontology_coverage = self._clip(inputs.get("ontology_coverage", 0.5))
        novelty_detection_quality = self._clip(
            inputs.get("novelty_detection_quality", 0.5)
        )
        scientific_value_estimation = self._clip(
            inputs.get("scientific_value_estimation", 0.5)
        )
        architectural_value_estimation = self._clip(
            inputs.get("architectural_value_estimation", 0.5)
        )
        feasibility_assessment = self._clip(
            inputs.get("feasibility_assessment", 0.5)
        )
        strategic_alignment = self._clip(
            inputs.get("strategic_alignment", 0.5)
        )

        open_ended_capability_discovery_index = self._clip(
            0.15 * ontology_coverage
            + 0.15 * novelty_detection_quality
            + 0.20 * scientific_value_estimation
            + 0.20 * architectural_value_estimation
            + 0.15 * feasibility_assessment
            + 0.15 * strategic_alignment
        )

        if open_ended_capability_discovery_index >= 0.95:
            discovery_class = "canonical_open_ended_discovery"
        elif open_ended_capability_discovery_index >= 0.85:
            discovery_class = "high_fidelity_open_ended_discovery"
        elif open_ended_capability_discovery_index >= 0.70:
            discovery_class = "functional_open_ended_discovery"
        else:
            discovery_class = "partial_open_ended_discovery"

        return {
            "open_ended_capability_discovery_index": round(
                open_ended_capability_discovery_index, 4
            ),
            "capability_discovery_score": round(
                open_ended_capability_discovery_index, 4
            ),
            "discovery_class": discovery_class,
        }
