from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as ROOT_INVENTORY
from ontology.ontology_inventory import (
    ONTOLOGY_INVENTORY as PACKAGE_INVENTORY,
)


assert ROOT_INVENTORY.count("bifurcation_detector") == 1
assert PACKAGE_INVENTORY.count("bifurcation_detector") == 1
assert "bifurcation_detector" in DEPENDENCY_REGISTRY

dependencies = DEPENDENCY_REGISTRY["bifurcation_detector"]

required = {
    "developmental_blueprint",
    "genesis_detector",
    "maturation_tracker",
    "specialization_engine",
    "regime_transition_detector",
    "trajectory_bifurcation",
    "trajectory_phase_transition",
    "trajectory_attractor_transition",
    "structural_transition_operator",
    "structural_attractor",
    "attractor_persistence_analyzer",
    "longitudinal_drift_detection",
    "consciousness_longitudinal_tracker",
    "reflexive_stability_monitor",
    "evidence_quality_assessment",
    "false_positive_detector",
}

assert required.issubset(set(dependencies))
assert len(dependencies) == len(set(dependencies))

print("AV4_REGISTRY_INTEGRITY_OK")
