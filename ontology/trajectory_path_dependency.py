'''
Trajectory path dependency.

Property by which the current and future evolution of a trajectory
depends on the sequence of states and transitions previously traversed.
'''

PRIMITIVE = "trajectory_path_dependency"

DESCRIPTION = (
    "Dependence of trajectory evolution on its historical sequence "
    "of states and transitions."
)

DEPENDENCIES = [
    "trajectory_hysteresis",
    "trajectory_regime",
]


class TrajectoryPathDependency:
    """Auto-generated activation class for trajectory_path_dependency."""

    PRIMITIVE = "trajectory_path_dependency"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

