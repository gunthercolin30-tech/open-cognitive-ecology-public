'''
Trajectory preference shaping.

Formation and adjustment of preference structures that bias
goal-conditioned trajectory selection.
'''

PRIMITIVE = "trajectory_preference_shaping"

DESCRIPTION = (
    "Shaping of preference structures influencing goal-conditioned "     "trajectory selection."
)

DEPENDENCIES = [
    "trajectory_goal_conditioning",
]


class TrajectoryPreferenceShaping:
    """Auto-generated activation class for trajectory_preference_shaping."""

    PRIMITIVE = "trajectory_preference_shaping"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

