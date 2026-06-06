from __future__ import annotations

PRIMITIVE = "homeostatic_regulation"
DESCRIPTION = "Homeostatic regulation."
DEPENDENCIES = []

"""
ontology/homeostatic_regulation.py

Scientific implementation of the HOMEOSTATIC_REGULATION primitive.

HOMEOSTATIC_REGULATION quantifies the capacity of a system to detect
deviations from viable operating ranges and deploy corrective responses
that restore stable functioning.

Dimensions:
- deviation_detection
- corrective_response
- setpoint_stability
- homeostatic_regulation_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "HOMEOSTATIC_REGULATION"
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


class HomeostaticRegulation:
    """
    Deviation detection and corrective stabilization capacity.
    """

    def __init__(
        self,
        deviation_detection=0.0,
        corrective_response=0.0,
        setpoint_stability=0.0,
    ):
        self.deviation_detection = _clamp(deviation_detection)
        self.corrective_response = _clamp(corrective_response)
        self.setpoint_stability = _clamp(setpoint_stability)

    def evaluate(self, state=None):
        """
        Evaluate homeostatic regulation metrics.

        Parameters
        ----------
        state : dict or None
            Optional override values:
            - deviation_detection
            - corrective_response
            - setpoint_stability
        """
        state = state or {}

        dd = _clamp(state.get("deviation_detection", self.deviation_detection))
        cr = _clamp(state.get("corrective_response", self.corrective_response))
        ss = _clamp(state.get("setpoint_stability", self.setpoint_stability))

        homeostatic_regulation_index = (dd + cr + ss) / 3.0
        status = "active" if homeostatic_regulation_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "deviation_detection": dd,
            "corrective_response": cr,
            "setpoint_stability": ss,
            "status": status,
        }

        return {
            "deviation_detection": dd,
            "corrective_response": cr,
            "setpoint_stability": ss,
            "homeostatic_regulation_index": homeostatic_regulation_index,
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
        index = result["homeostatic_regulation_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "homeostatic_regulation_index": index,
            "diagnostics": result["diagnostics"],
        }
