from __future__ import annotations

PRIMITIVE = "allostatic_adaptation"
DESCRIPTION = "Allostatic adaptation."
DEPENDENCIES = []

"""
ontology/allostatic_adaptation.py

Scientific implementation of the ALLOSTATIC_ADAPTATION primitive.

ALLOSTATIC_ADAPTATION quantifies the capacity of a system to dynamically
adjust its internal setpoints and regulatory norms in anticipation of
contextual changes.

Dimensions:
- setpoint_adjustment
- predictive_compensation
- contextual_reconfiguration
- allostatic_adaptation_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "ALLOSTATIC_ADAPTATION"
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


class AllostaticAdaptation:
    """
    Dynamic setpoint adjustment and predictive regulation.
    """

    def __init__(
        self,
        setpoint_adjustment=0.0,
        predictive_compensation=0.0,
        contextual_reconfiguration=0.0,
    ):
        self.setpoint_adjustment = _clamp(setpoint_adjustment)
        self.predictive_compensation = _clamp(predictive_compensation)
        self.contextual_reconfiguration = _clamp(contextual_reconfiguration)

    def evaluate(self, state=None):
        """
        Evaluate allostatic adaptation metrics.
        """
        state = state or {}

        sa = _clamp(state.get("setpoint_adjustment", self.setpoint_adjustment))
        pc = _clamp(
            state.get("predictive_compensation", self.predictive_compensation)
        )
        cr = _clamp(
            state.get(
                "contextual_reconfiguration",
                self.contextual_reconfiguration,
            )
        )

        allostatic_adaptation_index = (sa + pc + cr) / 3.0
        status = "active" if allostatic_adaptation_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "setpoint_adjustment": sa,
            "predictive_compensation": pc,
            "contextual_reconfiguration": cr,
            "status": status,
        }

        return {
            "setpoint_adjustment": sa,
            "predictive_compensation": pc,
            "contextual_reconfiguration": cr,
            "allostatic_adaptation_index": allostatic_adaptation_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["allostatic_adaptation_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "allostatic_adaptation_index": index,
            "diagnostics": result["diagnostics"],
        }
