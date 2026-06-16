from ontology.constitutional_evolution_gate import (
    DEPENDENCIES as EVOLUTION_GATE_DEPENDENCIES,
)
from ontology.constitutional_self_modification_protocol import (
    DEPENDENCIES as SELF_MODIFICATION_DEPENDENCIES,
)
from ontology.controlled_evolution_orchestrator import (
    DEPENDENCIES as ORCHESTRATOR_DEPENDENCIES,
)
from ontology.evolution_sandbox import DEPENDENCIES as SANDBOX_DEPENDENCIES
from ontology.recursive_self_improvement_controller import (
    DEPENDENCIES as CONTROLLER_DEPENDENCIES,
)


def test_controlled_evolution_orchestrator_consumes_governed_results():
    assert "evolution_sandbox" in ORCHESTRATOR_DEPENDENCIES
    assert "recursive_self_improvement_controller" in ORCHESTRATOR_DEPENDENCIES
    assert "constitutional_evolution_gate" in ORCHESTRATOR_DEPENDENCIES
    assert "constitutional_self_modification_protocol" in ORCHESTRATOR_DEPENDENCIES

    assert "controlled_evolution_orchestrator" not in CONTROLLER_DEPENDENCIES
    assert "controlled_evolution_orchestrator" not in EVOLUTION_GATE_DEPENDENCIES
    assert "controlled_evolution_orchestrator" not in SELF_MODIFICATION_DEPENDENCIES
    assert "controlled_evolution_orchestrator" not in SANDBOX_DEPENDENCIES
