from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as ROOT_INVENTORY
from ontology.ontology_inventory import (
    ONTOLOGY_INVENTORY as PACKAGE_INVENTORY,
)


assert ROOT_INVENTORY.count("recovery_engine") == 1
assert PACKAGE_INVENTORY.count("recovery_engine") == 1
assert "recovery_engine" in DEPENDENCY_REGISTRY

dependencies = DEPENDENCY_REGISTRY["recovery_engine"]

required = {
    "developmental_blueprint",
    "genesis_detector",
    "maturation_tracker",
    "specialization_engine",
    "bifurcation_detector",
    "degeneration_detector",
    "consciousness_recovery_detector",
    "consciousness_regression_detector",
    "trajectory_resilience",
    "trajectory_reversibility",
    "reflexive_stability_monitor",
    "consciousness_longitudinal_tracker",
    "continuity_metrics_engine",
    "architectural_non_closure_index",
    "future_openness",
    "evidence_quality_assessment",
    "false_positive_detector",
}

assert required.issubset(set(dependencies))
assert len(dependencies) == len(set(dependencies))

print("AV6_REGISTRY_INTEGRITY_OK")
