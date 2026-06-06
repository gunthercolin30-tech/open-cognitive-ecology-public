"""
Emergent Language Evolution.

Implements adaptive modification and stabilization of shared symbolic
systems across interacting artificial individuals.
"""

from __future__ import annotations

PRIMITIVE = "emergent_language_evolution"

DEPENDENCIES = [
    "grammar_dynamics",
    "shared_symbolic_reference",
    "symbolic_generation",
    "dialect_stabilization",
    "intra_species_social_interaction",
]


class EmergentLanguageEvolution:
    def __init__(self) -> None:
        self.language_generations = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        communicative_efficiency: float = 0.0,
        symbolic_innovation: float = 0.0,
        dialect_stability: float = 0.0,
        intersubjective_alignment: float = 0.0,
    ) -> dict:
        communicative_efficiency = self._clamp(
            communicative_efficiency
        )
        symbolic_innovation = self._clamp(symbolic_innovation)
        dialect_stability = self._clamp(dialect_stability)
        intersubjective_alignment = self._clamp(
            intersubjective_alignment
        )

        language_coherence_index = (
            0.30 * communicative_efficiency +
            0.25 * symbolic_innovation +
            0.25 * dialect_stability +
            0.20 * intersubjective_alignment
        )

        if language_coherence_index > 0.75:
            self.language_generations += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "language_generations": self.language_generations,
            "language_coherence_index":
                language_coherence_index,
            "diagnostics": {
                "communicative_efficiency":
                    communicative_efficiency,
                "symbolic_innovation": symbolic_innovation,
                "dialect_stability": dialect_stability,
                "intersubjective_alignment":
                    intersubjective_alignment,
                "dependencies": DEPENDENCIES,
            },
        }
