'''
Trajectory decision policy.

Operational rule that maps learned evaluations, constraints, and
preferences to an effective trajectory choice.
'''

PRIMITIVE = "trajectory_decision_policy"

DESCRIPTION = (
    "Decision policy selecting effective trajectories from learned " 
    "evaluations and exploration/exploitation balance."
)

DEPENDENCIES = [
    "trajectory_learning",
    "trajectory_exploration_exploitation_balance",
]


class TrajectoryDecisionPolicy:
    """Auto-generated activation class for trajectory_decision_policy."""

    PRIMITIVE = "trajectory_decision_policy"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

