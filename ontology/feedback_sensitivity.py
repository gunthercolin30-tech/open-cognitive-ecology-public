from __future__ import annotations

PRIMITIVE = "feedback_sensitivity"
DESCRIPTION = "Feedback sensitivity."
DEPENDENCIES = []

"""
ontology/feedback_sensitivity.py

Scientific implementation of the FEEDBACK_SENSITIVITY primitive.

FEEDBACK_SENSITIVITY quantifies the degree to which a system detects,
amplifies and uses feedback signals to correct deviations and improve
its behavior.

Dimensions:
- signal_detection
- response_gain
- error_correction_efficiency
- feedback_sensitivity_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "FEEDBACK_SENSITIVITY"
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


class FeedbackSensitivity:
    """
    Sensitivity and responsiveness to corrective feedback.
    """

    def __init__(
        self,
        signal_detection=0.0,
        response_gain=0.0,
        error_correction_efficiency=0.0,
    ):
        self.signal_detection = _clamp(signal_detection)
        self.response_gain = _clamp(response_gain)
        self.error_correction_efficiency = _clamp(
            error_correction_efficiency
        )

    def evaluate(self, state=None):
        """
        Evaluate feedback sensitivity metrics.
        """
        state = state or {}

        sd = _clamp(state.get("signal_detection", self.signal_detection))
        rg = _clamp(state.get("response_gain", self.response_gain))
        ece = _clamp(
            state.get(
                "error_correction_efficiency",
                self.error_correction_efficiency,
            )
        )

        feedback_sensitivity_index = (sd + rg + ece) / 3.0
        status = "active" if feedback_sensitivity_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "signal_detection": sd,
            "response_gain": rg,
            "error_correction_efficiency": ece,
            "status": status,
        }

        return {
            "signal_detection": sd,
            "response_gain": rg,
            "error_correction_efficiency": ece,
            "feedback_sensitivity_index": feedback_sensitivity_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["feedback_sensitivity_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "feedback_sensitivity_index": index,
            "diagnostics": result["diagnostics"],
        }
