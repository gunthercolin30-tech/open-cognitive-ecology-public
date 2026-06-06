from __future__ import annotations

PRIMITIVE = "navigability"
DESCRIPTION = "Navigability."
DEPENDENCIES = []

"""
ontology/navigability.py

Scientific implementation of the NAVIGABILITY primitive.

NAVIGABILITY quantifies the practical capacity of a system to follow
viable trajectories through an accessible state space.

Dimensions:
- path_guidance
- trajectory_stability
- decision_resolution
- navigability_index

All numerical quantities are bounded in [0, 1].
"""


PRIMITIVE_NAME = "NAVIGABILITY"
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


class Navigability:
    """
    Practical ability to navigate along viable paths.
    """

    def __init__(
        self,
        path_guidance=0.0,
        trajectory_stability=0.0,
        decision_resolution=0.0,
    ):
        self.path_guidance = _clamp(path_guidance)
        self.trajectory_stability = _clamp(trajectory_stability)
        self.decision_resolution = _clamp(decision_resolution)

    def evaluate(self, state=None):
        state = state or {}

        pg = _clamp(state.get("path_guidance", self.path_guidance))
        ts = _clamp(
            state.get("trajectory_stability", self.trajectory_stability)
        )
        dr = _clamp(
            state.get("decision_resolution", self.decision_resolution)
        )

        navigability_index = (pg + ts + dr) / 3.0
        status = "active" if navigability_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "path_guidance": pg,
            "trajectory_stability": ts,
            "decision_resolution": dr,
            "status": status,
        }

        return {
            "path_guidance": pg,
            "trajectory_stability": ts,
            "decision_resolution": dr,
            "navigability_index": navigability_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["navigability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "navigability_index": index,
            "diagnostics": result["diagnostics"],
        }
