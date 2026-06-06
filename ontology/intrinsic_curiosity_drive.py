"""
Intrinsic Curiosity Drive.

Implements a functional intrinsic motivation mechanism that increases
exploration pressure when novelty and uncertainty are high.
"""

from __future__ import annotations

PRIMITIVE = "intrinsic_curiosity_drive"

DEPENDENCIES = [
    "novelty_emergence",
    "uncertainty_awareness",
    "autonomous_world_exploration_engine",
    "affective_valuation_system",
    "exploration_exploitation_balance",
]


class IntrinsicCuriosityDrive:
    def __init__(self) -> None:
        self.update_count = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        novelty: float = 0.0,
        uncertainty: float = 0.0,
        learning_progress: float = 0.0,
        affective_salience: float = 0.0,
    ) -> dict:
        novelty = self._clamp(novelty)
        uncertainty = self._clamp(uncertainty)
        learning_progress = self._clamp(learning_progress)
        affective_salience = self._clamp(affective_salience)

        curiosity_pressure = (
            0.35 * novelty +
            0.30 * uncertainty +
            0.20 * learning_progress +
            0.15 * affective_salience
        )

        intrinsic_curiosity_index = (
            curiosity_pressure + learning_progress
        ) / 2.0

        self.update_count += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "update_count": self.update_count,
            "curiosity_pressure": curiosity_pressure,
            "intrinsic_curiosity_index": intrinsic_curiosity_index,
            "diagnostics": {
                "novelty": novelty,
                "uncertainty": uncertainty,
                "learning_progress": learning_progress,
                "affective_salience": affective_salience,
                "dependencies": DEPENDENCIES,
            },
        }
