from __future__ import annotations

PRIMITIVE = "controllability"
DESCRIPTION = "Controllability."
DEPENDENCIES = []

"""
ontology/controllability.py

Scientific implementation of the CONTROLLABILITY primitive.

CONTROLLABILITY quantifies the capacity of a system to reach desired
internal states using available actuation and control channels.

Dimensions:
- actuation_reach
- state_accessibility
- control_effectiveness
- controllability_index

All numerical quantities are bounded in [0, 1].
"""



PRIMITIVE_NAME = "CONTROLLABILITY"
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


class Controllability:
    """
    Reachability of internal states through available controls.
    """

    def __init__(
        self,
        actuation_reach=0.0,
        state_accessibility=0.0,
        control_effectiveness=0.0,
    ):
        self.actuation_reach = _clamp(actuation_reach)
        self.state_accessibility = _clamp(state_accessibility)
        self.control_effectiveness = _clamp(control_effectiveness)

    def evaluate(self, state=None):
        """
        Evaluate controllability metrics.
        """
        state = state or {}

        ar = _clamp(state.get("actuation_reach", self.actuation_reach))
        sa = _clamp(
            state.get("state_accessibility", self.state_accessibility)
        )
        ce = _clamp(
            state.get("control_effectiveness", self.control_effectiveness)
        )

        controllability_index = (ar + sa + ce) / 3.0
        status = "active" if controllability_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "actuation_reach": ar,
            "state_accessibility": sa,
            "control_effectiveness": ce,
            "status": status,
        }

        return {
            "actuation_reach": ar,
            "state_accessibility": sa,
            "control_effectiveness": ce,
            "controllability_index": controllability_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["controllability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "controllability_index": index,
            "diagnostics": result["diagnostics"],
        }
