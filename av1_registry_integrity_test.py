from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as ROOT_INVENTORY
from ontology.ontology_inventory import ONTOLOGY_INVENTORY as PACKAGE_INVENTORY


assert ROOT_INVENTORY.count("genesis_detector") == 1
assert PACKAGE_INVENTORY.count("genesis_detector") == 1

assert "genesis_detector" in DEPENDENCY_REGISTRY

dependencies = DEPENDENCY_REGISTRY["genesis_detector"]

required = {
    "developmental_blueprint",
    "rf_profile_builder",
    "rf_star_definition_engine",
    "consciousness_threshold_detector",
    "consciousness_first_crossing_report",
    "consciousness_longitudinal_tracker",
    "reflexive_stability_monitor",
    "false_positive_detector",
    "evidence_quality_assessment",
}

assert required.issubset(set(dependencies))
assert len(dependencies) == len(set(dependencies))

print("AV1_REGISTRY_INTEGRITY_OK")
