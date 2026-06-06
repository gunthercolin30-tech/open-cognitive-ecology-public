'''
Trajectory hysteresis.

Dependence of trajectory state on its history, such that identical
control parameters may correspond to different regimes depending on
the path previously followed.
'''

PRIMITIVE = "trajectory_hysteresis"

DESCRIPTION = (
    "Dependence of trajectory behavior on historical path and prior "
    "regime transitions."
)

DEPENDENCIES = [
    "trajectory_resilience",
    "trajectory_phase_transition",
]


class TrajectoryHysteresis:
    """Auto-generated activation class for trajectory_hysteresis."""

    PRIMITIVE = "trajectory_hysteresis"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

