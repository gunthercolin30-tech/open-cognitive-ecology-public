'''
Trajectory attractor transition.

Transition in which a trajectory leaves one basin of attraction
and becomes captured by a distinct attractor.
'''

PRIMITIVE = "trajectory_attractor_transition"

DESCRIPTION = (
    "Transition between distinct attractors in trajectory space."
)

DEPENDENCIES = [
    "trajectory_cascade",
    "trajectory_regime",
]


class TrajectoryAttractorTransition:
    """Auto-generated activation class for trajectory_attractor_transition."""

    PRIMITIVE = "trajectory_attractor_transition"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

