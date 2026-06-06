from __future__ import annotations

PRIMITIVE = "free_energy_minimization"
DESCRIPTION = "Free energy minimization."
DEPENDENCIES = []

"""
FREE_ENERGY_MINIMIZATION primitive.

This module formalizes the principle that adaptive systems preserve viability by
reducing discrepancies between internal predictions and observations. The
primitive integrates prediction accuracy, model evidence, and uncertainty
reduction.

The primitive computes:
- prediction_accuracy
- model_evidence
- uncertainty_reduction
- free_energy_minimization_index
"""


PRIMITIVE_NAME = "FREE_ENERGY_MINIMIZATION"
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


class FreeEnergyMinimization:
    """Formal model of adaptive inference through free energy reduction."""

    def __init__(
        self,
        accuracy_weight=1.0,
        evidence_weight=1.0,
        uncertainty_weight=1.0,
    ):
        self.accuracy_weight = max(0.0, float(accuracy_weight))
        self.evidence_weight = max(0.0, float(evidence_weight))
        self.uncertainty_weight = max(0.0, float(uncertainty_weight))

    def evaluate(
        self,
        prediction_accuracy=0.0,
        model_evidence=0.0,
        uncertainty_reduction=0.0,
    ):
        prediction_accuracy = _clamp(prediction_accuracy)
        model_evidence = _clamp(model_evidence)
        uncertainty_reduction = _clamp(uncertainty_reduction)

        total_weight = (
            self.accuracy_weight
            + self.evidence_weight
            + self.uncertainty_weight
        )

        if total_weight <= 0.0:
            free_energy_minimization_index = 0.0
        else:
            free_energy_minimization_index = (
                self.accuracy_weight * prediction_accuracy
                + self.evidence_weight * model_evidence
                + self.uncertainty_weight * uncertainty_reduction
            ) / total_weight

        free_energy_minimization_index = _clamp(
            free_energy_minimization_index
        )

        is_empty = (
            prediction_accuracy == 0.0
            and model_evidence == 0.0
            and uncertainty_reduction == 0.0
        )

        return {
            "prediction_accuracy": prediction_accuracy,
            "model_evidence": model_evidence,
            "uncertainty_reduction": uncertainty_reduction,
            "free_energy_minimization_index":
                free_energy_minimization_index,
            "diagnostics": {
                "primitive": PRIMITIVE_NAME,
                "accuracy_weight": self.accuracy_weight,
                "evidence_weight": self.evidence_weight,
                "uncertainty_weight": self.uncertainty_weight,
                "status": "empty_input" if is_empty else "evaluated",
            },
        }

    def step(
        self,
        prediction_accuracy=0.0,
        model_evidence=0.0,
        uncertainty_reduction=0.0,
    ):
        return self.evaluate(
            prediction_accuracy,
            model_evidence,
            uncertainty_reduction,
        )

    def validate(
        self,
        prediction_accuracy=0.0,
        model_evidence=0.0,
        uncertainty_reduction=0.0,
    ):
        result = self.evaluate(
            prediction_accuracy,
            model_evidence,
            uncertainty_reduction,
        )

        index_ = result["free_energy_minimization_index"]

        return {
            "is_valid": index_ > 0.0,
            "free_energy_minimization_index": index_,
            "diagnostics": result["diagnostics"],
        }
