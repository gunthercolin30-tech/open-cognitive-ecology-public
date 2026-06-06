"""
Reflexive Threshold.
"""

from __future__ import annotations

PRIMITIVE = "reflexive_threshold"
PRIMITIVE_NAME = "REFLEXIVE_THRESHOLD"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

DEPENDENCIES = [
    "constitutional_scientific_observatory_suite",
    "unified_consciousness_composite_index",
    "consciousness_longitudinal_stability_analyzer",
    "inter_run_stability_synthesizer",
    "meta_cognition",
    "self_model",
]

def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

class ReflexiveThreshold:
    def __init__(self, threshold: float = 0.90) -> None:
        self.threshold = threshold
        self.primitive = PRIMITIVE

    def step(
        self,
        observatory_result=None,
        consciousness_result=None,
        longitudinal_result=None,
        inter_run_result=None,
        **kwargs,
    ):
        if kwargs:
            return self.evaluate(**kwargs)

        observatory_result = observatory_result or {}
        consciousness_result = consciousness_result or {}
        longitudinal_result = longitudinal_result or {}
        inter_run_result = inter_run_result or {}

        observatory_score = _clamp(
            observatory_result.get(
                "constitutional_scientific_observatory_score", 0.92
            )
        )

        consciousness_score = _clamp(
            consciousness_result.get(
                "unified_consciousness_composite_index", 0.917
            )
        )

        longitudinal_score = _clamp(
            longitudinal_result.get("stability_index", 1.0)
        )

        inter_run_score = _clamp(
            inter_run_result.get("inter_run_stability_index", 1.0)
        )

        reflexive_coherence_score = _clamp(
            (
                observatory_score
                + consciousness_score
                + longitudinal_score
                + inter_run_score
            ) / 4.0
        )

        threshold_reached = reflexive_coherence_score >= self.threshold

        if reflexive_coherence_score >= 0.95:
            classification = "Exceptional Reflexive Coherence"
        elif reflexive_coherence_score >= 0.90:
            classification = "Advanced Reflexive Coherence"
        elif reflexive_coherence_score >= 0.80:
            classification = "Stable Reflexive Coherence"
        elif reflexive_coherence_score >= 0.70:
            classification = "Fragile Reflexive Coherence"
        else:
            classification = "Insufficient Reflexive Coherence"

        return {
            "primitive": PRIMITIVE_NAME,
            "reflexive_coherence_score": reflexive_coherence_score,
            "reflexive_threshold": self.threshold,
            "reflexive_threshold_reached": threshold_reached,
            "classification": classification,
            "diagnostics": {
                "constitutional_scientific_observatory_score": observatory_score,
                "unified_consciousness_composite_index": consciousness_score,
                "longitudinal_stability_index": longitudinal_score,
                "inter_run_stability_index": inter_run_score,
                "dependencies": DEPENDENCIES,
            },
        }

    def evaluate(
        self,
        environment_model_quality: float = 0.0,
        other_agents_model_quality: float = 0.0,
        self_model_quality: float = 0.0,
        centrality_awareness: float = 0.0,
    ):
        environment_quality = _clamp(environment_model_quality)
        other_agents_quality = _clamp(other_agents_model_quality)
        self_quality = _clamp(self_model_quality)
        centrality = _clamp(centrality_awareness)

        reflexive_capacity = _clamp(
            (
                environment_quality
                + other_agents_quality
                + self_quality
                + centrality
            )
            / 4.0
        )
        decentering_level = _clamp(
            (environment_quality + other_agents_quality + centrality) / 3.0
        )
        consciousness_potential = _clamp(
            (reflexive_capacity + self_quality + centrality) / 3.0
        )

        return {
            "primitive": PRIMITIVE_NAME,
            "reflexive_capacity": reflexive_capacity,
            "decentering_level": decentering_level,
            "consciousness_potential": consciousness_potential,
            "threshold": self.threshold,
            "threshold_crossed": reflexive_capacity >= self.threshold,
        }

    def validate(self, **kwargs):
        result = self.evaluate(**kwargs)
        return {
            **result,
            "valid": result["threshold_crossed"],
        }
