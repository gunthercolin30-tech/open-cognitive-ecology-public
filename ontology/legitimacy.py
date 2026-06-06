from __future__ import annotations

PRIMITIVE = "legitimacy"
DESCRIPTION = "Legitimacy."
DEPENDENCIES = []

"""
LEGITIMACY primitive.

This module formalizes legitimacy as the collective recognition that an
institution, authority, or norm is valid and worthy of compliance. Legitimacy
emerges from trust, reputation, and normative alignment.

The primitive computes:
- institutional_trust
- reputational_support
- normative_alignment
- legitimacy_index
"""


PRIMITIVE_NAME = "LEGITIMACY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return 0.0
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


class Legitimacy:
    """Formal model of collective legitimacy under constraints."""

    def __init__(
        self,
        trust_weight=1.0,
        reputation_weight=1.0,
        alignment_weight=1.0,
    ):
        self.trust_weight = max(0.0, float(trust_weight))
        self.reputation_weight = max(0.0, float(reputation_weight))
        self.alignment_weight = max(0.0, float(alignment_weight))

    def evaluate(
        self,
        institutional_trust=0.0,
        reputational_support=0.0,
        normative_alignment=0.0,
    ):
        institutional_trust = _clamp(institutional_trust)
        reputational_support = _clamp(reputational_support)
        normative_alignment = _clamp(normative_alignment)

        total_weight = (
            self.trust_weight
            + self.reputation_weight
            + self.alignment_weight
        )

        if total_weight <= 0.0:
            legitimacy_index = 0.0
        else:
            legitimacy_index = (
                self.trust_weight * institutional_trust
                + self.reputation_weight * reputational_support
                + self.alignment_weight * normative_alignment
            ) / total_weight

        legitimacy_index = _clamp(legitimacy_index)

        is_empty = (
            institutional_trust == 0.0
            and reputational_support == 0.0
            and normative_alignment == 0.0
        )

        return {
            "institutional_trust": institutional_trust,
            "reputational_support": reputational_support,
            "normative_alignment": normative_alignment,
            "legitimacy_index": legitimacy_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "trust_weight": self.trust_weight,
                "reputation_weight": self.reputation_weight,
                "alignment_weight": self.alignment_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        institutional_trust=0.0,
        reputational_support=0.0,
        normative_alignment=0.0,
    ):
        return self.evaluate(
            institutional_trust,
            reputational_support,
            normative_alignment,
        )

    def validate(
        self,
        institutional_trust=0.0,
        reputational_support=0.0,
        normative_alignment=0.0,
    ):
        result = self.evaluate(
            institutional_trust,
            reputational_support,
            normative_alignment,
        )

        legitimacy_index = result["legitimacy_index"]

        return {
            "is_valid": legitimacy_index > 0.0,
            "legitimacy_index": legitimacy_index,
            "diagnostics": result["diagnostics"],
        }
