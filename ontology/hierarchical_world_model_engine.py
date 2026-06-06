"""
HIERARCHICAL_WORLD_MODEL_ENGINE

Builds a hierarchical model of the world by integrating local, mesoscopic,
and global representations into a unified predictive structure.
"""

from typing import Dict, Any


class HierarchicalWorldModelEngine:
    """Computes a composite hierarchical world-model quality index."""

    def _clip(self, x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        local_model_quality = self._clip(inputs.get("local_model_quality", 0.5))
        mesoscopic_model_quality = self._clip(inputs.get("mesoscopic_model_quality", 0.5))
        global_model_quality = self._clip(inputs.get("global_model_quality", 0.5))
        causal_consistency = self._clip(inputs.get("causal_consistency", 0.5))
        predictive_accuracy = self._clip(inputs.get("predictive_accuracy", 0.5))
        planning_utility = self._clip(inputs.get("planning_utility", 0.5))

        scale_integration_score = self._clip(
            0.30 * local_model_quality
            + 0.35 * mesoscopic_model_quality
            + 0.35 * global_model_quality
        )

        world_model_coherence = self._clip(
            0.40 * scale_integration_score
            + 0.20 * causal_consistency
            + 0.20 * predictive_accuracy
            + 0.20 * planning_utility
        )

        if world_model_coherence >= 0.95:
            model_class = "canonical_hierarchical_world_model"
        elif world_model_coherence >= 0.85:
            model_class = "high_fidelity_world_model"
        elif world_model_coherence >= 0.70:
            model_class = "functional_world_model"
        else:
            model_class = "partial_world_model"

        return {
            "scale_integration_score": round(scale_integration_score, 4),
            "world_model_coherence": round(world_model_coherence, 4),
            "predictive_environment_model_index": round(world_model_coherence, 4),
            "model_class": model_class,
        }
