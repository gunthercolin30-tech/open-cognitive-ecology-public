"""
UNIFIED_CIVILIZATIONAL_CONTROL_CENTER

Aggregates core civilizational indices into a unified supervisory control layer.
"""

from typing import Dict, Any


class UnifiedCivilizationalControlCenter:
    """Computes a unified global supervisory index."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        scientific_autonomy_score = self._clip(
            inputs.get("scientific_autonomy_score", 0.5)
        )
        civilizational_persistence_score = self._clip(
            inputs.get("civilizational_persistence_score", 0.5)
        )
        species_strategy_score = self._clip(
            inputs.get("species_strategy_score", 0.5)
        )
        cosmological_readiness_score = self._clip(
            inputs.get("cosmological_readiness_score", 0.5)
        )
        constitutional_integrity = self._clip(
            inputs.get("constitutional_integrity", 0.5)
        )
        unified_consciousness_index = self._clip(
            inputs.get("unified_consciousness_index", 0.5)
        )

        unified_civilizational_control_index = self._clip(
            0.18 * scientific_autonomy_score
            + 0.18 * civilizational_persistence_score
            + 0.16 * species_strategy_score
            + 0.16 * cosmological_readiness_score
            + 0.16 * constitutional_integrity
            + 0.16 * unified_consciousness_index
        )

        if unified_civilizational_control_index >= 0.95:
            control_class = "canonical_unified_control"
        elif unified_civilizational_control_index >= 0.85:
            control_class = "high_fidelity_unified_control"
        elif unified_civilizational_control_index >= 0.70:
            control_class = "functional_unified_control"
        else:
            control_class = "partial_unified_control"

        return {
            "unified_civilizational_control_index": round(
                unified_civilizational_control_index, 4
            ),
            "global_supervisory_score": round(
                unified_civilizational_control_index, 4
            ),
            "control_class": control_class,
        }
