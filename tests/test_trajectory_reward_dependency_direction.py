from ontology.trajectory_outcome_evaluation import (
    DEPENDENCIES as OUTCOME_EVALUATION_DEPENDENCIES,
)
from ontology.trajectory_reward_assignment import (
    DEPENDENCIES as REWARD_ASSIGNMENT_DEPENDENCIES,
)


def test_outcome_evaluation_consumes_reward_assignment():
    assert "trajectory_reward_assignment" in OUTCOME_EVALUATION_DEPENDENCIES
    assert "trajectory_outcome_evaluation" not in REWARD_ASSIGNMENT_DEPENDENCIES
