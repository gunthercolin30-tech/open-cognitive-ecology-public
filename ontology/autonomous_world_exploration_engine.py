"""
Autonomous World Exploration Engine.

High-level orchestration primitive enabling self-directed exploration of
the environment through model-based hypothesis generation, strategy
selection, and learning updates.

This module does not claim phenomenological consciousness. It only
implements observable functional indicators of autonomous exploratory
behavior.
"""

from __future__ import annotations

PRIMITIVE = "autonomous_world_exploration_engine"

DEPENDENCIES = [
    "world_model",
    "counterfactual_simulation",
    "possible_worlds_navigation",
    "trajectory_strategy_selection",
    "learning",
]


class AutonomousWorldExplorationEngine:
    def __init__(self) -> None:
        self.cycle_count = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        novelty_signal: float = 0.0,
        uncertainty_level: float = 0.0,
        strategy_quality: float = 0.0,
        learning_progress: float = 0.0,
        world_model_coherence: float = 0.0,
    ) -> dict:
        novelty_signal = self._clamp(novelty_signal)
        uncertainty_level = self._clamp(uncertainty_level)
        strategy_quality = self._clamp(strategy_quality)
        learning_progress = self._clamp(learning_progress)
        world_model_coherence = self._clamp(world_model_coherence)

        exploratory_drive = (
            0.35 * novelty_signal +
            0.25 * uncertainty_level +
            0.20 * strategy_quality +
            0.20 * world_model_coherence
        )

        exploration_effectiveness = (
            0.50 * exploratory_drive +
            0.50 * learning_progress
        )

        autonomous_world_exploration_index = (
            exploratory_drive + exploration_effectiveness
        ) / 2.0

        self.cycle_count += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "cycle_count": self.cycle_count,
            "exploratory_drive": exploratory_drive,
            "exploration_effectiveness": exploration_effectiveness,
            "autonomous_world_exploration_index":
                autonomous_world_exploration_index,
            "diagnostics": {
                "novelty_signal": novelty_signal,
                "uncertainty_level": uncertainty_level,
                "strategy_quality": strategy_quality,
                "learning_progress": learning_progress,
                "world_model_coherence": world_model_coherence,
                "dependencies": DEPENDENCIES,
            },
        }
