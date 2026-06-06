'''
Trajectory horizon planning.

Construction of multi-scale plans over extended temporal horizons
by integrating predictive models, scheduling constraints, and
strategy selection.
'''

PRIMITIVE = "trajectory_horizon_planning"

DESCRIPTION = (
    "Construction of extended-horizon trajectory plans from " \
    "prediction, scheduling, and strategy selection."
)

DEPENDENCIES = [
    "trajectory_prediction",
    "trajectory_scheduling",
    "trajectory_strategy_selection",
]


class TrajectoryHorizonPlanning:
    """Auto-generated activation class for trajectory_horizon_planning."""

    PRIMITIVE = "trajectory_horizon_planning"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

