'''
Trajectory outcome evaluation.

Assessment of the consequences produced by executed actions
relative to goals, constraints, and expectations.
'''

PRIMITIVE = "trajectory_outcome_evaluation"

DESCRIPTION = (
    "Evaluation of executed action outcomes against goals, " \
    "constraints, and expectations."
)

DEPENDENCIES = [
    "trajectory_action_execution",
]


class TrajectoryOutcomeEvaluation:
    """Auto-generated activation class for trajectory_outcome_evaluation."""

    PRIMITIVE = "trajectory_outcome_evaluation"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

