"""
EMPIRICAL_CONSCIOUSNESS_EVIDENCE_SYNTHESIZER

Aggregates experimental evidence related to functional consciousness,
stability, and autonomy into a unified empirical synthesis.
"""

from typing import Dict, Any


class EmpiricalConsciousnessEvidenceSynthesizer:
    """Computes consolidated empirical consciousness evidence metrics."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        empirical_validation_score = self._clip(
            inputs.get("empirical_validation_score", 0.5)
        )
        unified_consciousness_index = self._clip(
            inputs.get("unified_consciousness_index", 0.5)
        )
        functional_stability = self._clip(
            inputs.get("functional_stability", 0.5)
        )
        autonomy_consistency = self._clip(
            inputs.get("autonomy_consistency", 0.5)
        )
        longitudinal_reproducibility = self._clip(
            inputs.get("longitudinal_reproducibility", 0.5)
        )
        theoretical_convergence = self._clip(
            inputs.get("theoretical_convergence", 0.5)
        )

        empirical_consciousness_evidence_index = self._clip(
            0.20 * empirical_validation_score
            + 0.20 * unified_consciousness_index
            + 0.15 * functional_stability
            + 0.15 * autonomy_consistency
            + 0.15 * longitudinal_reproducibility
            + 0.15 * theoretical_convergence
        )

        if empirical_consciousness_evidence_index >= 0.95:
            evidence_class = "canonical_empirical_consciousness_evidence"
        elif empirical_consciousness_evidence_index >= 0.85:
            evidence_class = "high_fidelity_empirical_consciousness_evidence"
        elif empirical_consciousness_evidence_index >= 0.70:
            evidence_class = "functional_empirical_consciousness_evidence"
        else:
            evidence_class = "partial_empirical_consciousness_evidence"

        return {
            "empirical_consciousness_evidence_index": round(
                empirical_consciousness_evidence_index, 4
            ),
            "functional_consciousness_evidence_score": round(
                empirical_consciousness_evidence_index, 4
            ),
            "evidence_class": evidence_class,
        }
