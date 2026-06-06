from __future__ import annotations

PRIMITIVE = "anti_fragility"
DESCRIPTION = "Anti fragility."
DEPENDENCIES = []

"""
ontology/anti_fragility.py

Scientific implementation of the ANTI_FRAGILITY primitive.

ANTI_FRAGILITY quantifies the capacity of a system to improve its
performance and adaptive potential in response to perturbations and stress.

Dimensions:
- stress_gain
- adaptive_improvement
- beneficial_variation_capture
- anti_fragility_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "ANTI_FRAGILITY"
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


class AntiFragility:
    """
    Capacity to improve under perturbation and uncertainty.
    """

    def __init__(
        self,
        stress_gain=0.0,
        adaptive_improvement=0.0,
        beneficial_variation_capture=0.0,
    ):
        self.stress_gain = _clamp(stress_gain)
        self.adaptive_improvement = _clamp(adaptive_improvement)
        self.beneficial_variation_capture = _clamp(
            beneficial_variation_capture
        )

    def evaluate(self, state=None):
        """
        Evaluate anti-fragility metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - stress_gain
            - adaptive_improvement
            - beneficial_variation_capture
        """
        state = state or {}

        sg = _clamp(state.get("stress_gain", self.stress_gain))
        ai = _clamp(
            state.get("adaptive_improvement", self.adaptive_improvement)
        )
        bvc = _clamp(
            state.get(
                "beneficial_variation_capture",
                self.beneficial_variation_capture,
            )
        )

        anti_fragility_index = (sg + ai + bvc) / 3.0
        status = "active" if anti_fragility_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "stress_gain": sg,
            "adaptive_improvement": ai,
            "beneficial_variation_capture": bvc,
            "status": status,
        }

        return {
            "stress_gain": sg,
            "adaptive_improvement": ai,
            "beneficial_variation_capture": bvc,
            "anti_fragility_index": anti_fragility_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        """
        One-step operational interface equivalent to evaluate().
        """
        return self.evaluate(state)

    def validate(self, state=None):
        """
        Validate structural consistency of the primitive.
        """
        result = self.evaluate(state)
        index = result["anti_fragility_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "anti_fragility_index": index,
            "diagnostics": result["diagnostics"],
        }
