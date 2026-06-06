'''
Trajectory exploration.

Active search for new trajectories and viable regions to acquire
information and discover improved behaviors under constraints.
'''

PRIMITIVE = "trajectory_exploration"

DESCRIPTION = (
    "Active search for novel trajectories and viable regions."
)

DEPENDENCIES = [
    "trajectory_learning",
    "trajectory_adaptation",
]


class TrajectoryExploration:
    """Auto-generated activation class for trajectory_exploration."""

    PRIMITIVE = "trajectory_exploration"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

