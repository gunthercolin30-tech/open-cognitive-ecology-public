"""
Offline Dream Simulation.

Implements offline generative simulation cycles for memory consolidation,
counterfactual recombination, and exploratory restructuring.
"""

from __future__ import annotations

PRIMITIVE = "offline_dream_simulation"

DEPENDENCIES = [
    "memory_consolidation",
    "counterfactual_simulation",
    "imagination",
    "possible_worlds_generation",
    "intrinsic_curiosity_drive",
]


class OfflineDreamSimulation:
    def __init__(self) -> None:
        self.dream_cycle_count = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        memory_salience: float = 0.0,
        recombination_novelty: float = 0.0,
        simulation_coherence: float = 0.0,
        insight_generation: float = 0.0,
    ) -> dict:
        memory_salience = self._clamp(memory_salience)
        recombination_novelty = self._clamp(recombination_novelty)
        simulation_coherence = self._clamp(simulation_coherence)
        insight_generation = self._clamp(insight_generation)

        dream_intensity = (
            0.30 * memory_salience +
            0.25 * recombination_novelty +
            0.25 * simulation_coherence +
            0.20 * insight_generation
        )

        offline_dream_simulation_index = (
            dream_intensity + insight_generation
        ) / 2.0

        self.dream_cycle_count += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "dream_cycle_count": self.dream_cycle_count,
            "dream_intensity": dream_intensity,
            "offline_dream_simulation_index":
                offline_dream_simulation_index,
            "diagnostics": {
                "memory_salience": memory_salience,
                "recombination_novelty": recombination_novelty,
                "simulation_coherence": simulation_coherence,
                "insight_generation": insight_generation,
                "dependencies": DEPENDENCIES,
            },
        }
