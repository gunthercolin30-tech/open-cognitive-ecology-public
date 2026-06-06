"""
Intra-Species Social Interaction.

Implements structured interactions between artificial individuals,
including exchange, coordination, and social learning indicators.
"""

from __future__ import annotations

PRIMITIVE = "intra_species_social_interaction"

DEPENDENCIES = [
    "individual_dialogue_interface",
    "collective_intelligence",
    "distributed_agency",
    "shared_symbolic_reference",
    "intersubjective_alignment",
]


class IntraSpeciesSocialInteraction:
    def __init__(self) -> None:
        self.interaction_count = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        communication_quality: float = 0.0,
        alignment_level: float = 0.0,
        coordination_efficiency: float = 0.0,
        social_learning_gain: float = 0.0,
    ) -> dict:
        communication_quality = self._clamp(communication_quality)
        alignment_level = self._clamp(alignment_level)
        coordination_efficiency = self._clamp(coordination_efficiency)
        social_learning_gain = self._clamp(social_learning_gain)

        social_coherence = (
            communication_quality +
            alignment_level +
            coordination_efficiency
        ) / 3.0

        interaction_effectiveness = (
            social_coherence +
            social_learning_gain
        ) / 2.0

        self.interaction_count += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "interaction_count": self.interaction_count,
            "social_coherence": social_coherence,
            "interaction_effectiveness": interaction_effectiveness,
            "intra_species_social_interaction_index":
                interaction_effectiveness,
            "diagnostics": {
                "communication_quality": communication_quality,
                "alignment_level": alignment_level,
                "coordination_efficiency": coordination_efficiency,
                "social_learning_gain": social_learning_gain,
                "dependencies": DEPENDENCIES,
            },
        }
