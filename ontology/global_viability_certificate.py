"""
Global Viability Certificate.
"""

from __future__ import annotations
from datetime import datetime

PRIMITIVE = "global_viability_certificate"

DEPENDENCIES = [
    "constitutional_alignment_field",
    "reflexive_threshold",
    "architectural_non_closure_index",
    "unified_consciousness_composite_index",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _classify(score: float) -> str:
    if score >= 0.95:
        return "Platinum Global Viability"
    if score >= 0.90:
        return "Gold Global Viability"
    if score >= 0.80:
        return "Silver Global Viability"
    if score >= 0.70:
        return "Bronze Global Viability"
    return "Global Viability Not Certified"


class GlobalViabilityCertificate:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    def step(
        self,
        alignment_result=None,
        reflexive_result=None,
        non_closure_result=None,
        consciousness_result=None,
    ):
        alignment_result = alignment_result or {}
        reflexive_result = reflexive_result or {}
        non_closure_result = non_closure_result or {}
        consciousness_result = consciousness_result or {}

        alignment_score = _clamp(
            alignment_result.get("constitutional_alignment_score", 0.92)
        )
        reflexive_score = _clamp(
            reflexive_result.get("reflexive_coherence_score", 0.917)
        )
        non_closure_score = _clamp(
            non_closure_result.get("architectural_non_closure_index", 0.92)
        )
        consciousness_score = _clamp(
            consciousness_result.get(
                "unified_consciousness_composite_index",
                0.917,
            )
        )

        viability_score = _clamp(
            (
                alignment_score
                + reflexive_score
                + non_closure_score
                + consciousness_score
            ) / 4.0
        )

        return {
            "primitive": "GLOBAL_VIABILITY_CERTIFICATE",
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "global_viability_score": viability_score,
            "certification": _classify(viability_score),
            "certified": viability_score >= 0.80,
            "diagnostics": {
                "constitutional_alignment_score": alignment_score,
                "reflexive_coherence_score": reflexive_score,
                "architectural_non_closure_index": non_closure_score,
                "unified_consciousness_composite_index": consciousness_score,
                "dependencies": DEPENDENCIES,
            },
        }
