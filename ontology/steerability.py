from __future__ import annotations

PRIMITIVE = "steerability"
DESCRIPTION = "Steerability."
DEPENDENCIES = []

"""
ontology/steerability.py

Scientific implementation of the STEERABILITY primitive.

STEERABILITY quantifies the capacity of a system to actively reorient
its trajectory in response to feedback, constraints, and goals.

Dimensions:
- directional_control
- trajectory_reorientation
- constraint_responsive_steering
- steerability_index

All numerical quantities are bounded in [0, 1].
"""


PRIMITIVE_NAME = "STEERABILITY"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def _clamp(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


class Steerability:
    """
    Capacity to dynamically redirect a viable trajectory.
    """

    def __init__(
        self,
        directional_control=0.0,
        trajectory_reorientation=0.0,
        constraint_responsive_steering=0.0,
    ):
        self.directional_control = _clamp(directional_control)
        self.trajectory_reorientation = _clamp(trajectory_reorientation)
        self.constraint_responsive_steering = _clamp(
            constraint_responsive_steering
        )

    def evaluate(self, state=None):
        state = state or {}

        dc = _clamp(
            state.get("directional_control", self.directional_control)
        )
        tr = _clamp(
            state.get(
                "trajectory_reorientation",
                self.trajectory_reorientation,
            )
        )
        crs = _clamp(
            state.get(
                "constraint_responsive_steering",
                self.constraint_responsive_steering,
            )
        )

        steerability_index = (dc + tr + crs) / 3.0
        status = "active" if steerability_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "directional_control": dc,
            "trajectory_reorientation": tr,
            "constraint_responsive_steering": crs,
            "status": status,
        }

        return {
            "directional_control": dc,
            "trajectory_reorientation": tr,
            "constraint_responsive_steering": crs,
            "steerability_index": steerability_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["steerability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "steerability_index": index,
            "diagnostics": result["diagnostics"],
        }
