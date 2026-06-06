from __future__ import annotations

PRIMITIVE = "goal_directedness"
DESCRIPTION = "Goal directedness."
DEPENDENCIES = []

"""
ontology/goal_directedness.py

Scientific implementation of the GOAL_DIRECTEDNESS primitive.

GOAL_DIRECTEDNESS quantifies the extent to which a system's dynamics
are organized toward preferred target states.

Dimensions:
- target_specification
- objective_persistence
- trajectory_alignment
- goal_directedness_index

All numerical quantities are bounded in [0, 1].
"""


PRIMITIVE_NAME = "GOAL_DIRECTEDNESS"
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


class GoalDirectedness:
    """
    Degree of orientation toward preferred target states.
    """

    def __init__(
        self,
        target_specification=0.0,
        objective_persistence=0.0,
        trajectory_alignment=0.0,
    ):
        self.target_specification = _clamp(target_specification)
        self.objective_persistence = _clamp(objective_persistence)
        self.trajectory_alignment = _clamp(trajectory_alignment)

    def evaluate(self, state=None):
        state = state or {}

        ts = _clamp(
            state.get("target_specification", self.target_specification)
        )
        op = _clamp(
            state.get("objective_persistence", self.objective_persistence)
        )
        ta = _clamp(
            state.get("trajectory_alignment", self.trajectory_alignment)
        )

        goal_directedness_index = (ts + op + ta) / 3.0
        status = "active" if goal_directedness_index > 0.0 else "inactive"

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "target_specification": ts,
            "objective_persistence": op,
            "trajectory_alignment": ta,
            "status": status,
        }

        return {
            "target_specification": ts,
            "objective_persistence": op,
            "trajectory_alignment": ta,
            "goal_directedness_index": goal_directedness_index,
            "diagnostics": diagnostics,
        }

    def step(self, state=None):
        return self.evaluate(state)

    def validate(self, state=None):
        result = self.evaluate(state)
        index = result["goal_directedness_index"]

        return {
            "is_valid": 0.0 <= index <= 1.0,
            "goal_directedness_index": index,
            "diagnostics": result["diagnostics"],
        }
