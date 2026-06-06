'''
Trajectory action selection.

Translation of goal-conditioned preferences and strategies into
concrete actions selected for execution.
'''

PRIMITIVE = "trajectory_action_selection"

DESCRIPTION = (
    "Selection of concrete actions from shaped preferences and " \
    "goal-conditioned trajectory strategies."
)

DEPENDENCIES = [
    "trajectory_preference_shaping",
]


class TrajectoryActionSelection:
    """Auto-generated activation class for trajectory_action_selection."""

    PRIMITIVE = "trajectory_action_selection"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

