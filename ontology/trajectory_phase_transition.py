PRIMITIVE = "trajectory_phase_transition"
DESCRIPTION = "Trajectory phase transition."
DEPENDENCIES = []

"""Trajectory phase transitions under constraints."""

CONCEPT = "trajectory_phase_transition"

DESCRIPTION = (
    "Describes qualitative regime changes in the dynamics of trajectories "
    "when control parameters cross critical thresholds."
)


class TrajectoryPhaseTransition:
    """Auto-generated activation class for trajectory_phase_transition."""

    PRIMITIVE = "trajectory_phase_transition"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

