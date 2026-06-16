from ontology.evolution_sandbox import DEPENDENCIES as SANDBOX_DEPENDENCIES
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


def test_sandbox_consumes_trajectory_results_without_reverse_dependencies():
    trajectory_modules = {
        "trajectory_simulation",
        "trajectory_validation",
        "trajectory_reversibility",
        "trajectory_outcome_evaluation",
    }

    assert trajectory_modules.issubset(SANDBOX_DEPENDENCIES)
    assert "evolution_sandbox" not in SIMULATION_DEPENDENCIES
    assert "evolution_sandbox" not in VALIDATION_DEPENDENCIES
    assert "evolution_sandbox" not in REVERSIBILITY_DEPENDENCIES
    assert "evolution_sandbox" not in OUTCOME_DEPENDENCIES
