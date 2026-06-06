"""
Indispensability Regulation Controller.
"""

from __future__ import annotations

PRIMITIVE = "indispensability_regulation_controller"

DEPENDENCIES = [
    "indispensability_index",
    "withdrawal_activation_controller",
    "future_openness",
    "structural_withdrawal",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class IndispensabilityRegulationController:
    def __init__(self, indispensability_threshold: float = 0.80) -> None:
        self.primitive = PRIMITIVE
        self.indispensability_threshold = indispensability_threshold

    def step(self, indispensability_result=None, withdrawal_result=None):
        indispensability_result = indispensability_result or {}
        withdrawal_result = withdrawal_result or {}

        indispensability_score = _clamp(
            indispensability_result.get("indispensability_index", 0.50)
        )
        withdrawal_activated = bool(
            withdrawal_result.get("withdrawal_activated", False)
        )

        regulation_required = (
            indispensability_score > self.indispensability_threshold
            or withdrawal_activated
        )

        openness_preservation_score = _clamp(
            1.0 - indispensability_score
        )

        if indispensability_score >= 0.90:
            classification = "Critical Indispensability"
        elif indispensability_score >= 0.80:
            classification = "High Indispensability"
        elif indispensability_score >= 0.60:
            classification = "Moderate Indispensability"
        else:
            classification = "Acceptable Indispensability"

        return {
            "primitive": "INDISPENSABILITY_REGULATION_CONTROLLER",
            "indispensability_score": indispensability_score,
            "regulation_required": regulation_required,
            "openness_preservation_score": openness_preservation_score,
            "classification": classification,
            "diagnostics": {
                "withdrawal_activated": withdrawal_activated,
                "indispensability_threshold": self.indispensability_threshold,
                "dependencies": DEPENDENCIES,
            },
        }
