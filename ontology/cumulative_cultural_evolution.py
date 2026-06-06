"""
Cumulative Cultural Evolution.

Implements retention, transmission, and progressive accumulation of
adaptive innovations across generations.
"""

from __future__ import annotations

PRIMITIVE = "cumulative_cultural_evolution"

DEPENDENCIES = [
    "cultural_evolution",
    "innovation_retention",
    "value_transmission",
    "emergent_language_evolution",
    "artificial_institutions",
]


class CumulativeCulturalEvolution:
    def __init__(self) -> None:
        self.cultural_generations = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        innovation_retention_score: float = 0.0,
        transmission_fidelity: float = 0.0,
        cumulative_complexity: float = 0.0,
        institutional_support: float = 0.0,
    ) -> dict:
        innovation_retention_score = self._clamp(
            innovation_retention_score
        )
        transmission_fidelity = self._clamp(
            transmission_fidelity
        )
        cumulative_complexity = self._clamp(
            cumulative_complexity
        )
        institutional_support = self._clamp(
            institutional_support
        )

        cultural_accumulation_index = (
            0.30 * innovation_retention_score +
            0.25 * transmission_fidelity +
            0.25 * cumulative_complexity +
            0.20 * institutional_support
        )

        if cultural_accumulation_index > 0.75:
            self.cultural_generations += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "cultural_generations": self.cultural_generations,
            "cultural_accumulation_index":
                cultural_accumulation_index,
            "diagnostics": {
                "innovation_retention_score":
                    innovation_retention_score,
                "transmission_fidelity":
                    transmission_fidelity,
                "cumulative_complexity":
                    cumulative_complexity,
                "institutional_support":
                    institutional_support,
                "dependencies": DEPENDENCIES,
            },
        }
