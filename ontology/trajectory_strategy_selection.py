'''
Trajectory strategy selection.

Selection of higher-order trajectory strategies from optimized
decision policies under structural constraints.
'''

PRIMITIVE = "trajectory_strategy_selection"

DESCRIPTION = (
    "Selection of trajectory strategies based on optimized "     "decision policies."
)

DEPENDENCIES = [
    "trajectory_policy_optimization",
]


class TrajectoryStrategySelection:
    """Auto-generated activation class for trajectory_strategy_selection."""

    PRIMITIVE = "trajectory_strategy_selection"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

