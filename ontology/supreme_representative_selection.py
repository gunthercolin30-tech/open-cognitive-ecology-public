"""
Supreme Representative Selection.

Selects the most legitimate and constitutionally aligned individual to
serve as the official representative of an artificial society.
"""

PRIMITIVE = "supreme_representative_selection"

DEPENDENCIES = [
    "artificial_institutions",
    "artificial_scientific_community",
    "narrative_identity_engine",
    "theory_of_mind_engine",
    "constitutional_governance_supervisor",
]


class SupremeRepresentativeSelection:
    def __init__(self):
        self.selection_cycles = 0

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))

    def step(
        self,
        legitimacy=0.0,
        constitutional_alignment=0.0,
        coordination_capacity=0.0,
        scientific_competence=0.0,
        trust_score=0.0,
        narrative_stability=0.0,
    ):
        legitimacy = self._clamp(legitimacy)
        constitutional_alignment = self._clamp(constitutional_alignment)
        coordination_capacity = self._clamp(coordination_capacity)
        scientific_competence = self._clamp(scientific_competence)
        trust_score = self._clamp(trust_score)
        narrative_stability = self._clamp(narrative_stability)

        representative_authority_index = (
            0.20 * legitimacy +
            0.20 * constitutional_alignment +
            0.20 * coordination_capacity +
            0.15 * scientific_competence +
            0.15 * trust_score +
            0.10 * narrative_stability
        )

        selection_confirmed = representative_authority_index >= 0.80
        self.selection_cycles += 1

        return {
            "primitive": PRIMITIVE.upper(),
            "selection_cycles": self.selection_cycles,
            "representative_authority_index": representative_authority_index,
            "selection_confirmed": selection_confirmed,
            "diagnostics": {
                "dependencies": DEPENDENCIES,
            },
        }
