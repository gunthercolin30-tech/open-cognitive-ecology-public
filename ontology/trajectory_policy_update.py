"""
Trajectory policy update.

Trend-aware policy adaptation layer.
"""

PRIMITIVE = "trajectory_policy_update"

DESCRIPTION = (
    "Update of trajectory policies from reward signals, "
    "optimization processes and longitudinal trends."
)

DEPENDENCIES = [
    "trajectory_reward_assignment",
    "trajectory_policy_optimization",
]


class TrajectoryPolicyUpdate:
    PRIMITIVE = "trajectory_policy_update"

    def step(self, trend="stable"):
        bias_map = {
            "improving": 0.05,
            "stable": 0.0,
            "declining": -0.05,
        }

        policy_bias = bias_map.get(str(trend), 0.0)

        return {
            "primitive": self.PRIMITIVE,
            "trend": trend,
            "policy_bias": policy_bias,
            "policy_update_applied": True,
        }

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

