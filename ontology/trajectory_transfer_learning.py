'''
Trajectory transfer learning.

Reuse of knowledge acquired in previous trajectories to accelerate
adaptation and learning in new contexts.
'''

PRIMITIVE = "trajectory_transfer_learning"

DESCRIPTION = (
    "Transfer of learned trajectory structures across contexts to "
    "improve adaptation."
)

DEPENDENCIES = [
    "trajectory_learning",
    "trajectory_meta_learning",
]


class TrajectoryTransferLearning:
    """Auto-generated activation class for trajectory_transfer_learning."""

    PRIMITIVE = "trajectory_transfer_learning"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

