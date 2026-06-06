from __future__ import annotations

PRIMITIVE = "trust"
DESCRIPTION = "Trust."
DEPENDENCIES = []

"""
TRUST primitive.

This module formalizes trust as a structural reduction of uncertainty about the
future behavior of another agent or institution. Trust emerges when observed
behavior is consistent, predictive expectations are reliable, and institutional
support reinforces confidence.

The primitive computes:
- predictive_reliability
- behavioral_consistency
- institutional_confidence
- trust_index
"""


PRIMITIVE_NAME = "TRUST"
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


class Trust:
    """Formal model of trust under constraints."""

    def __init__(
        self,
        reliability_weight=1.0,
        consistency_weight=1.0,
        confidence_weight=1.0,
    ):
        self.reliability_weight = max(0.0, float(reliability_weight))
        self.consistency_weight = max(0.0, float(consistency_weight))
        self.confidence_weight = max(0.0, float(confidence_weight))

    def evaluate(
        self,
        expected_behavior=None,
        observed_behavior=None,
        institutional_support=0.0,
    ):
        expected = list(expected_behavior or [])
        observed = list(observed_behavior or [])

        if not expected or not observed:
            predictive_reliability = 0.0
            behavioral_consistency = 0.0
        else:
            n = min(len(expected), len(observed))
            expected = [_clamp(v) for v in expected[:n]]
            observed = [_clamp(v) for v in observed[:n]]

            mean_abs_error = sum(
                abs(a - b) for a, b in zip(expected, observed)
            ) / n

            predictive_reliability = _clamp(1.0 - mean_abs_error)
            behavioral_consistency = _clamp(1.0 - mean_abs_error)

        institutional_confidence = _clamp(institutional_support)

        total_weight = (
            self.reliability_weight
            + self.consistency_weight
            + self.confidence_weight
        )

        if total_weight <= 0.0:
            trust_index = 0.0
        else:
            trust_index = (
                self.reliability_weight * predictive_reliability
                + self.consistency_weight * behavioral_consistency
                + self.confidence_weight * institutional_confidence
            ) / total_weight

        trust_index = _clamp(trust_index)

        return {
            "predictive_reliability": predictive_reliability,
            "behavioral_consistency": behavioral_consistency,
            "institutional_confidence": institutional_confidence,
            "trust_index": trust_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "reliability_weight": self.reliability_weight,
                "consistency_weight": self.consistency_weight,
                "confidence_weight": self.confidence_weight,
                "status": (
                    "empty_input"
                    if not expected_behavior or not observed_behavior
                    else "evaluated"
                ),
            },
        }

    def step(
        self,
        expected_behavior=None,
        observed_behavior=None,
        institutional_support=0.0,
    ):
        return self.evaluate(
            expected_behavior,
            observed_behavior,
            institutional_support,
        )

    def validate(
        self,
        expected_behavior=None,
        observed_behavior=None,
        institutional_support=0.0,
    ):
        result = self.evaluate(
            expected_behavior,
            observed_behavior,
            institutional_support,
        )
        trust_index = result["trust_index"]
        return {
            "is_valid": trust_index > 0.0,
            "trust_index": trust_index,
            "diagnostics": result["diagnostics"],
        }
