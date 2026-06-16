from ontology.trajectory_outcome_evaluation import (
    DEPENDENCIES as OUTCOME_DEPENDENCIES,
)
from ontology.trajectory_reversibility import (
    DEPENDENCIES as REVERSIBILITY_DEPENDENCIES,
)
from ontology.trajectory_simulation import (
    DEPENDENCIES as SIMULATION_DEPENDENCIES,
)
from ontology.trajectory_validation import (
    DEPENDENCIES as VALIDATION_DEPENDENCIES,
)


def test_trajectory_pipeline_dependencies_follow_consumer_order():
    assert "controlled_evolution_orchestrator" not in SIMULATION_DEPENDENCIES
    assert "controlled_evolution_orchestrator" not in VALIDATION_DEPENDENCIES
    assert "controlled_evolution_orchestrator" not in REVERSIBILITY_DEPENDENCIES
    assert "controlled_evolution_orchestrator" not in OUTCOME_DEPENDENCIES

    assert "trajectory_validation" in SIMULATION_DEPENDENCIES

    assert "trajectory_simulation" in REVERSIBILITY_DEPENDENCIES
    assert "trajectory_validation" in REVERSIBILITY_DEPENDENCIES

    assert "trajectory_simulation" in OUTCOME_DEPENDENCIES
    assert "trajectory_validation" in OUTCOME_DEPENDENCIES
    assert "trajectory_reversibility" in OUTCOME_DEPENDENCIES

    assert "trajectory_simulation" not in VALIDATION_DEPENDENCIES
    assert "trajectory_reversibility" not in VALIDATION_DEPENDENCIES
    assert "trajectory_outcome_evaluation" not in VALIDATION_DEPENDENCIES
    assert "trajectory_reversibility" not in SIMULATION_DEPENDENCIES
    assert "trajectory_outcome_evaluation" not in SIMULATION_DEPENDENCIES
    assert "trajectory_outcome_evaluation" not in REVERSIBILITY_DEPENDENCIES
