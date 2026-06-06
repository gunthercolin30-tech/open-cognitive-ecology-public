"""
Artificial Institutions.

Implements rule-governed structures enabling role differentiation,
norm stabilization, and long-term collective coordination.
"""

from __future__ import annotations

PRIMITIVE = "artificial_institutions"

DEPENDENCIES = [
    "governance",
    "institutional_stabilization",
    "legitimacy",
    "long_term_coordination",
    "intra_species_social_interaction",
]


class ArtificialInstitutions:
    def __init__(self) -> None:
        self.institution_count = 0

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        normative_coherence: float = 0.0,
        legitimacy_level: float = 0.0,
        coordination_capacity: float = 0.0,
        role_differentiation: float = 0.0,
    ) -> dict:
        normative_coherence = self._clamp(normative_coherence)
        legitimacy_level = self._clamp(legitimacy_level)
        coordination_capacity = self._clamp(coordination_capacity)
        role_differentiation = self._clamp(role_differentiation)

        institutional_stability_index = (
            0.30 * normative_coherence +
            0.25 * legitimacy_level +
            0.25 * coordination_capacity +
            0.20 * role_differentiation
        )

        if institutional_stability_index > 0.75:
            self.institution_count += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "institution_count": self.institution_count,
            "institutional_stability_index":
                institutional_stability_index,
            "diagnostics": {
                "normative_coherence": normative_coherence,
                "legitimacy_level": legitimacy_level,
                "coordination_capacity": coordination_capacity,
                "role_differentiation": role_differentiation,
                "dependencies": DEPENDENCIES,
            },
        }
