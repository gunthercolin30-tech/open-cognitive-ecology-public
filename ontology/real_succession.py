PRIMITIVE = "real_succession"
DESCRIPTION = "Real succession."
DEPENDENCIES = []

"""
ontology.real_succession
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RealSuccessionResult:
    valid: bool
    dna_conserved: bool
    continuity_score: float
    threshold: float
    diagnostics: Dict[str, Any]


class RealSuccessionPrimitive:
    primitive_name = "REAL_SUCCESSION"

    def __init__(self, continuity_threshold: float = 0.75):
        if not 0.0 <= continuity_threshold <= 1.0:
            raise ValueError("continuity_threshold must be between 0 and 1.")
        self.continuity_threshold = continuity_threshold

    def evaluate(self, ancestor: Any, descendant: Any) -> RealSuccessionResult:
        ancestor_dna = self._extract_minimal_dna(ancestor)
        descendant_dna = self._extract_minimal_dna(descendant)

        dna_conserved = (
            ancestor_dna is not None
            and descendant_dna is not None
            and ancestor_dna == descendant_dna
        )

        continuity_score = self._compute_continuity(ancestor, descendant)

        valid = (
            dna_conserved
            and continuity_score >= self.continuity_threshold
        )

        diagnostics = {
            "primitive": self.primitive_name,
            "dna_conserved": dna_conserved,
            "continuity_score": continuity_score,
            "continuity_threshold": self.continuity_threshold,
            "status": "valid" if valid else "invalid",
        }

        return RealSuccessionResult(
            valid=valid,
            dna_conserved=dna_conserved,
            continuity_score=continuity_score,
            threshold=self.continuity_threshold,
            diagnostics=diagnostics,
        )

    def validate(self, ancestor: Any, descendant: Any) -> bool:
        return self.evaluate(ancestor, descendant).valid

    def _extract_minimal_dna(self, entity: Any):
        if entity is None:
            return None

        if isinstance(entity, dict):
            return entity.get("minimal_dna")

        if hasattr(entity, "minimal_dna"):
            return getattr(entity, "minimal_dna")

        return None

    def _compute_continuity(self, ancestor: Any, descendant: Any) -> float:
        if not isinstance(ancestor, dict) or not isinstance(descendant, dict):
            return 0.0

        all_keys = set(ancestor.keys()) | set(descendant.keys())
        if not all_keys:
            return 1.0

        matches = 0
        for key in all_keys:
            if key in ancestor and key in descendant:
                if ancestor[key] == descendant[key]:
                    matches += 1

        return matches / len(all_keys)


def evaluate_real_succession(
    ancestor: Any,
    descendant: Any,
    continuity_threshold: float = 0.75,
) -> RealSuccessionResult:
    primitive = RealSuccessionPrimitive(
        continuity_threshold=continuity_threshold
    )
    return primitive.evaluate(ancestor, descendant)