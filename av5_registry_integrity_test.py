from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as ROOT_INVENTORY
from ontology.ontology_inventory import (
    ONTOLOGY_INVENTORY as PACKAGE_INVENTORY,
)


assert ROOT_INVENTORY.count("degeneration_detector") == 1
assert PACKAGE_INVENTORY.count("degeneration_detector") == 1
assert "degeneration_detector" in DEPENDENCY_REGISTRY

dependencies = DEPENDENCY_REGISTRY["degeneration_detector"]

required = {
    "developmental_blueprint",
    "genesis_detector",
    "maturation_tracker",
    "specialization_engine",
    "bifurcation_detector",
    "consciousness_regression_detector",
    "consciousness_recovery_detector",
    "reflexive_stability_monitor",
    "consciousness_longitudinal_tracker",
    "longitudinal_drift_detection",
    "continuity_metrics_engine",
    "composite_metrics_engine",
    "architectural_non_closure_index",
    "future_openness",
    "evidence_quality_assessment",
    "false_positive_detector",
}

assert required.issubset(set(dependencies))
assert len(dependencies) == len(set(dependencies))

print("AV5_REGISTRY_INTEGRITY_OK")
