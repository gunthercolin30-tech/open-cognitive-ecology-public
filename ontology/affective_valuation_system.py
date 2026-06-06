"""
Affective Valuation System.

Computes functional affective valuations that modulate priorities,
without asserting phenomenological feelings.
"""

from __future__ import annotations

PRIMITIVE = "affective_valuation_system"

DEPENDENCIES = [
    "preference",
    "value_formation",
    "global_experience_evaluation",
    "prioritization",
    "decision_making",
]


class AffectiveValuationSystem:
    def __init__(self) -> None:
        self.evaluation_count = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        desirability: float = 0.0,
        urgency: float = 0.0,
        uncertainty: float = 0.0,
        coherence: float = 0.0,
    ) -> dict:
        desirability = self._clamp(desirability)
        urgency = self._clamp(urgency)
        uncertainty = self._clamp(uncertainty)
        coherence = self._clamp(coherence)

        affective_salience = (
            0.35 * desirability +
            0.30 * urgency +
            0.20 * uncertainty +
            0.15 * coherence
        )

        affective_regulation_index = (
            affective_salience + coherence
        ) / 2.0

        self.evaluation_count += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "evaluation_count": self.evaluation_count,
            "affective_salience": affective_salience,
            "affective_regulation_index": affective_regulation_index,
            "diagnostics": {
                "desirability": desirability,
                "urgency": urgency,
                "uncertainty": uncertainty,
                "coherence": coherence,
                "dependencies": DEPENDENCIES,
            },
        }
