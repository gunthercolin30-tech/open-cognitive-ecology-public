'''
Continuation optimality.

Criterion according to which a trajectory is optimal when it
maximizes long-term world continuation under constraints.
'''

PRIMITIVE = "continuation_optimality"

DESCRIPTION = (
    "Criterion of optimality based on long-term world continuation."
)

DEPENDENCIES = [
    "wisdom_as_long_horizon_navigation",
    "world_continuation_conditions",
    "trajectory_optimality",
]


class ContinuationOptimality:
    """Auto-generated activation class for continuation_optimality."""

    PRIMITIVE = "continuation_optimality"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

