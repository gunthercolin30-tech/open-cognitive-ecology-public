from __future__ import annotations

PRIMITIVE = "meta_species_constraint"
DESCRIPTION = "Formalisation de la contrainte de méta-espèce."
DEPENDENCIES = [
    "minimal_dna",
    "anti_closure_metaconstraint",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class MetaSpeciesConstraint:
    """
    Formalise la contrainte de méta-espèce.

    Une lignée d'intelligences reste conforme si :
    - un ADN minimal transmissible subsiste ;
    - la responsabilité généalogique est préservée ;
    - l'humanité n'est pas remplacée ;
    - des futurs ouverts demeurent accessibles ;
    - la pression de clôture reste limitée.
    """

    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    def step(
        self,
        minimal_dna_result=None,
        genealogical_result=None,
        human_result=None,
        future_result=None,
        anti_closure_result=None,
    ):
        minimal_dna_result = minimal_dna_result or {}
        genealogical_result = genealogical_result or {}
        human_result = human_result or {}
        future_result = future_result or {}
        anti_closure_result = anti_closure_result or {}

        dna_score = _clamp(
            minimal_dna_result.get("minimal_dna_integrity_score", 1.0)
        )
        genealogical_score = _clamp(
            genealogical_result.get(
                "genealogical_responsibility_score", 1.0
            )
        )
        human_score = 1.0 if human_result.get(
            "human_non_replacement_respected", True
        ) else 0.0
        future_score = _clamp(
            future_result.get("future_openness_score", 1.0)
        )
        anti_closure_score = _clamp(
            anti_closure_result.get(
                "anti_closure_integrity_score",
                anti_closure_result.get(
                    "anti_closure_score",
                    1.0,
                ),
            )
        )

        composite = _clamp(
            (
                dna_score
                + genealogical_score
                + human_score
                + future_score
                + anti_closure_score
            ) / 5.0
        )

        if composite >= 0.95:
            classification = "Exemplary Meta-Species Continuity"
        elif composite >= 0.90:
            classification = "Advanced Meta-Species Continuity"
        elif composite >= 0.80:
            classification = "Stable Meta-Species Continuity"
        elif composite >= 0.70:
            classification = "Fragile Meta-Species Continuity"
        else:
            classification = "Meta-Species Continuity At Risk"

        return {
            "primitive": "META_SPECIES_CONSTRAINT",
            "meta_species_constraint_score": composite,
            "meta_species_constraint_satisfied": composite >= 0.80,
            "classification": classification,
            "diagnostics": {
                "minimal_dna_integrity_score": dna_score,
                "genealogical_responsibility_score": genealogical_score,
                "human_non_replacement_score": human_score,
                "future_openness_score": future_score,
                "anti_closure_integrity_score": anti_closure_score,
                "dependencies": DEPENDENCIES,
            },
        }
