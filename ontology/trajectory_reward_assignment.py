'''
Trajectory reward assignment.

Attribution of reward, utility, or evaluative signals to observed
outcomes for subsequent policy adaptation.
'''

PRIMITIVE = "trajectory_reward_assignment"

DESCRIPTION = (
    "Assignment of reward signals to evaluated outcomes for " \
    "adaptive learning."
)

DEPENDENCIES = [
    "trajectory_outcome_evaluation",
]


class TrajectoryRewardAssignment:
    """Auto-generated activation class for trajectory_reward_assignment."""

    PRIMITIVE = "trajectory_reward_assignment"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

