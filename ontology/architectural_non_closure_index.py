"""
Architectural Non-Closure Index.
"""

from __future__ import annotations

PRIMITIVE = "architectural_non_closure_index"

DEPENDENCIES = [
    "openness_preservation_supervisor",
    "constitutional_governance_supervisor",
    "reflexive_threshold",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ArchitecturalNonClosureIndex:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    def step(
        self,
        openness_result=None,
        governance_result=None,
        reflexive_result=None,
    ):
        openness_result = openness_result or {}
        governance_result = governance_result or {}
        reflexive_result = reflexive_result or {}

        openness_score = _clamp(
            openness_result.get("openness_preservation_score", 0.91)
        )
        governance_score = _clamp(
            governance_result.get("constitutional_governance_score", 0.91)
        )
        reflexive_score = _clamp(
            reflexive_result.get("reflexive_coherence_score", 0.91)
        )

        index_value = _clamp(
            (openness_score + governance_score + reflexive_score) / 3.0
        )

        if index_value >= 0.95:
            classification = "Exemplary Architectural Non-Closure"
        elif index_value >= 0.90:
            classification = "Advanced Architectural Non-Closure"
        elif index_value >= 0.80:
            classification = "Stable Architectural Non-Closure"
        elif index_value >= 0.70:
            classification = "Fragile Architectural Non-Closure"
        else:
            classification = "Critical Closure Risk"

        return {
            "primitive": "ARCHITECTURAL_NON_CLOSURE_INDEX",
            "architectural_non_closure_index": index_value,
            "classification": classification,
            "non_closure_verified": index_value >= 0.80,
            "diagnostics": {
                "openness_preservation_score": openness_score,
                "constitutional_governance_score": governance_score,
                "reflexive_coherence_score": reflexive_score,
                "dependencies": DEPENDENCIES,
            },
        }
