from __future__ import annotations

PRIMITIVE = "robustness"
DESCRIPTION = "Robustness."
DEPENDENCIES = []

"""
ontology/robustness.py

Scientific implementation of the ROBUSTNESS primitive.

ROBUSTNESS quantifies the structural capacity of a system to preserve
its functionality and viability under perturbations.

Dimensions:
- perturbation_tolerance
- functional_stability
- viability_preservation
- robustness_index

The robustness index is the arithmetic mean of the three dimensions.
All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "ROBUSTNESS"
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


class Robustness:
    """
    Structural preservation capacity under perturbation.
    """

    def __init__(
        self,
        perturbation_tolerance=0.0,
        functional_stability=0.0,
        viability_preservation=0.0,
    ):
        self.perturbation_tolerance = _clamp(perturbation_tolerance)
        self.functional_stability = _clamp(functional_stability)
        self.viability_preservation = _clamp(viability_preservation)

    def evaluate(self, state=None):
        """
        Evaluate robustness metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - perturbation_tolerance
            - functional_stability
            - viability_preservation
        """
        state = state or {}

        pt = _clamp(
            state.get("perturbation_tolerance", self.perturbation_tolerance)
        )
        fs = _clamp(
            state.get("functional_stability", self.functional_stability)
        )
        vp = _clamp(
            state.get("viability_preservation", self.viability_preservation)
        )

        robustness_index = (pt + fs + vp) / 3.0
        status = "active" if robustness_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "perturbation_tolerance": pt,
            "functional_stability": fs,
            "viability_preservation": vp,
            "status": status,
        }

        return {
            "perturbation_tolerance": pt,
            "functional_stability": fs,
            "viability_preservation": vp,
            "robustness_index": robustness_index,
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
        index = result["robustness_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "robustness_index": index,
            "diagnostics": result["diagnostics"],
        }
