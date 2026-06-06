from __future__ import annotations

PRIMITIVE = "reachability"
DESCRIPTION = "Reachability."
DEPENDENCIES = []

"""
ontology/reachability.py

Scientific implementation of the REACHABILITY primitive.
"""


PRIMITIVE_NAME = "REACHABILITY"
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


class Reachability:
    """
    Structural existence of viable paths toward target states.
    """

    def __init__(
        self,
        trajectory_existence=0.0,
        path_viability=0.0,
        target_connectivity=0.0,
    ):
        self.trajectory_existence = _clamp(trajectory_existence)
        self.path_viability = _clamp(path_viability)
        self.target_connectivity = _clamp(target_connectivity)

    def evaluate(self, state=None):
        state = state or {}

        te = _clamp(
            state.get("trajectory_existence", self.trajectory_existence)
        )
        pv = _clamp(state.get("path_viability", self.path_viability))
        tc = _clamp(
            state.get("target_connectivity", self.target_connectivity)
        )

        reachability_index = (te + pv + tc) / 3.0
        status = "active" if reachability_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "trajectory_existence": te,
            "path_viability": pv,
            "target_connectivity": tc,
            "status": status,
        }

        return {
            "trajectory_existence": te,
            "path_viability": pv,
            "target_connectivity": tc,
            "reachability_index": reachability_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["reachability_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "reachability_index": index,
            "diagnostics": result["diagnostics"],
        }
