'''
Trajectory goal conditioning.

Conditioning of trajectory strategies by explicit goals and
objective structures.
'''

PRIMITIVE = "trajectory_goal_conditioning"

DESCRIPTION = (
    "Conditioning of trajectory strategies according to explicit "     "goal structures."
)

DEPENDENCIES = [
    "trajectory_strategy_selection",
]


class TrajectoryGoalConditioning:
    """Auto-generated activation class for trajectory_goal_conditioning."""

    PRIMITIVE = "trajectory_goal_conditioning"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

