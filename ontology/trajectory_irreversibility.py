'''
Trajectory irreversibility.

Property of a trajectory for which a transition cannot be undone
without structural transformation, loss, or additional cost.
'''

PRIMITIVE = "trajectory_irreversibility"

DESCRIPTION = (
    "Property of a trajectory whose transitions cannot be fully "
    "reversed without structural cost."
)

DEPENDENCIES = [
    "trajectory_hysteresis",
    "trajectory_phase_transition",
]


class TrajectoryIrreversibility:
    """Auto-generated activation class for trajectory_irreversibility."""

    PRIMITIVE = "trajectory_irreversibility"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

