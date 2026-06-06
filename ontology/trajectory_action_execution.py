'''
Trajectory action execution.

Operational realization of selected actions within the environment
and constraint field.
'''

PRIMITIVE = "trajectory_action_execution"

DESCRIPTION = (
    "Execution of selected actions within environmental and " \
    "constraint conditions."
)

DEPENDENCIES = [
    "trajectory_action_selection",
]


class TrajectoryActionExecution:
    """Auto-generated activation class for trajectory_action_execution."""

    PRIMITIVE = "trajectory_action_execution"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

