from __future__ import annotations

PRIMITIVE = "reputation"
DESCRIPTION = "Reputation."
DEPENDENCIES = []

"""
REPUTATION primitive.

This module formalizes reputation as a collective memory of past behavioral
trajectories. Reputation aggregates historical reliability, social consensus,
and temporal stability to produce a durable expectation about future conduct.

The primitive computes:
- historical_reliability
- social_consensus
- reputation_stability
- reputation_index
"""


PRIMITIVE_NAME = "REPUTATION"
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


class Reputation:
    """Formal model of collective reputational assessment."""

    def __init__(
        self,
        reliability_weight=1.0,
        consensus_weight=1.0,
        stability_weight=1.0,
    ):
        self.reliability_weight = max(0.0, float(reliability_weight))
        self.consensus_weight = max(0.0, float(consensus_weight))
        self.stability_weight = max(0.0, float(stability_weight))

    def evaluate(
        self,
        historical_scores=None,
        social_assessments=None,
        temporal_consistency=0.0,
    ):
        history = [_clamp(v) for v in list(historical_scores or [])]
        assessments = [_clamp(v) for v in list(social_assessments or [])]

        historical_reliability = (
            sum(history) / len(history) if history else 0.0
        )

        social_consensus = (
            sum(assessments) / len(assessments) if assessments else 0.0
        )

        reputation_stability = _clamp(temporal_consistency)

        total_weight = (
            self.reliability_weight
            + self.consensus_weight
            + self.stability_weight
        )

        if total_weight <= 0.0:
            reputation_index = 0.0
        else:
            reputation_index = (
                self.reliability_weight * historical_reliability
                + self.consensus_weight * social_consensus
                + self.stability_weight * reputation_stability
            ) / total_weight

        reputation_index = _clamp(reputation_index)

        return {
            "historical_reliability": _clamp(historical_reliability),
            "social_consensus": _clamp(social_consensus),
            "reputation_stability": reputation_stability,
            "reputation_index": reputation_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "reliability_weight": self.reliability_weight,
                "consensus_weight": self.consensus_weight,
                "stability_weight": self.stability_weight,
                "status": (
                    "empty_input"
                    if not history and not assessments
                    and temporal_consistency == 0.0
                    else "evaluated"
                ),
            },
        }

    def step(
        self,
        historical_scores=None,
        social_assessments=None,
        temporal_consistency=0.0,
    ):
        return self.evaluate(
            historical_scores,
            social_assessments,
            temporal_consistency,
        )

    def validate(
        self,
        historical_scores=None,
        social_assessments=None,
        temporal_consistency=0.0,
    ):
        result = self.evaluate(
            historical_scores,
            social_assessments,
            temporal_consistency,
        )

        reputation_index = result["reputation_index"]

        return {
            "is_valid": reputation_index > 0.0,
            "reputation_index": reputation_index,
            "diagnostics": result["diagnostics"],
        }
