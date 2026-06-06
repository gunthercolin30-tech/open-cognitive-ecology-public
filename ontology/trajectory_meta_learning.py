'''
Trajectory meta-learning.

Optimization of the mechanisms of learning and adaptation based on
experience accumulated across multiple trajectories and contexts.
'''

PRIMITIVE = "trajectory_meta_learning"

DESCRIPTION = (
    "Learning how to improve learning and adaptation strategies "
    "across trajectories."
)

DEPENDENCIES = [
    "trajectory_learning",
    "trajectory_exploration",
    "meta_learning_optimizer",
    "trajectory_policy_optimization",
]


class TrajectoryMetaLearning:
    """Auto-generated activation class for trajectory_meta_learning."""

    PRIMITIVE = "trajectory_meta_learning"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

