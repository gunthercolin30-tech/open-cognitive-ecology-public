"""
Theory of Mind Engine.

Implements functional modeling of the beliefs, intentions, and
knowledge states of other artificial individuals.
"""

from __future__ import annotations

PRIMITIVE = "theory_of_mind_engine"

DEPENDENCIES = [
    "self_other_modeling",
    "intersubjective_alignment",
    "causal_inference",
    "intra_species_social_interaction",
    "individual_dialogue_interface",
]


class TheoryOfMindEngine:
    def __init__(self) -> None:
        self.inference_cycles = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        belief_prediction_accuracy: float = 0.0,
        intention_inference_accuracy: float = 0.0,
        perspective_differentiation: float = 0.0,
        social_context_understanding: float = 0.0,
    ) -> dict:
        belief_prediction_accuracy = self._clamp(
            belief_prediction_accuracy
        )
        intention_inference_accuracy = self._clamp(
            intention_inference_accuracy
        )
        perspective_differentiation = self._clamp(
            perspective_differentiation
        )
        social_context_understanding = self._clamp(
            social_context_understanding
        )

        theory_of_mind_index = (
            0.30 * belief_prediction_accuracy +
            0.25 * intention_inference_accuracy +
            0.25 * perspective_differentiation +
            0.20 * social_context_understanding
        )

        self.inference_cycles += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "inference_cycles": self.inference_cycles,
            "theory_of_mind_index": theory_of_mind_index,
            "diagnostics": {
                "belief_prediction_accuracy":
                    belief_prediction_accuracy,
                "intention_inference_accuracy":
                    intention_inference_accuracy,
                "perspective_differentiation":
                    perspective_differentiation,
                "social_context_understanding":
                    social_context_understanding,
                "dependencies": DEPENDENCIES,
            },
        }
