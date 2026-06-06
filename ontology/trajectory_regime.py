PRIMITIVE = "trajectory_regime"
DESCRIPTION = "Trajectory regime."
DEPENDENCIES = []

"""Dynamical regimes of trajectories under constraints."""

CONCEPT = "trajectory_regime"

DESCRIPTION = (
    "Describes qualitatively distinct classes of trajectory behavior such as "
    "stable, oscillatory, metastable, chaotic, and divergent regimes."
)


class TrajectoryRegime:
    """Auto-generated activation class for trajectory_regime."""

    PRIMITIVE = "trajectory_regime"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

