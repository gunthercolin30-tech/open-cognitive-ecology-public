'''
Trajectory reversibility.

Property of a trajectory for which transitions can be undone and
the system can return to a prior regime without structural loss.
'''

PRIMITIVE = "trajectory_reversibility"

DESCRIPTION = (
    "Property of a trajectory whose transitions can be reversed "
    "without structural cost."
)

DEPENDENCIES = [
    "trajectory_irreversibility",
    "trajectory_resilience",
]


class TrajectoryReversibility:
    """Auto-generated activation class for trajectory_reversibility."""

    PRIMITIVE = "trajectory_reversibility"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

