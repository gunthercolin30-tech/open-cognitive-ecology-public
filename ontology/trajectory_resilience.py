'''
Trajectory resilience.

Capacity of a trajectory to absorb perturbations and recover a viable
regime without undergoing an undesired phase transition.
'''

PRIMITIVE = "trajectory_resilience"

DESCRIPTION = (
    "Capacity of a trajectory to absorb perturbations and return "
    "to a viable regime."
)

DEPENDENCIES = [
    "trajectory_regime",
    "trajectory_metastability",
]


class TrajectoryResilience:
    """Auto-generated activation class for trajectory_resilience."""

    PRIMITIVE = "trajectory_resilience"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

