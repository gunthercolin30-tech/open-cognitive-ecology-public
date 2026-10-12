from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as ROOT_INVENTORY
from ontology.ontology_inventory import ONTOLOGY_INVENTORY as PACKAGE_INVENTORY


assert ROOT_INVENTORY.count("maturation_tracker") == 1
assert PACKAGE_INVENTORY.count("maturation_tracker") == 1

assert "maturation_tracker" in DEPENDENCY_REGISTRY

dependencies = DEPENDENCY_REGISTRY["maturation_tracker"]

required = {
    "developmental_blueprint",
    "genesis_detector",
    "consciousness_longitudinal_tracker",
    "reflexive_stability_monitor",
    "consciousness_regression_detector",
    "consciousness_recovery_detector",
    "continuity_metrics_engine",
    "composite_metrics_engine",
    "cognitive_diversity_preservation_protocol",
    "governance_consistency_checker",
    "evidence_quality_assessment",
}

assert required.issubset(set(dependencies))
assert len(dependencies) == len(set(dependencies))

print("AV2_REGISTRY_INTEGRITY_OK")
