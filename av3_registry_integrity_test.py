from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as ROOT_INVENTORY
from ontology.ontology_inventory import (
    ONTOLOGY_INVENTORY as PACKAGE_INVENTORY,
)


assert ROOT_INVENTORY.count("specialization_engine") == 1
assert PACKAGE_INVENTORY.count("specialization_engine") == 1
assert "specialization_engine" in DEPENDENCY_REGISTRY

dependencies = DEPENDENCY_REGISTRY["specialization_engine"]

required = {
    "developmental_blueprint",
    "genesis_detector",
    "maturation_tracker",
    "emergent_modularity",
    "collective_intelligence",
    "structural_attractor",
    "attractor_persistence_analyzer",
    "canalization",
    "degeneracy",
    "redundancy",
    "cognitive_diversity_preservation_protocol",
    "trajectory_reversibility",
    "trajectory_hysteresis",
    "non_closure",
    "architectural_non_closure_index",
    "future_openness",
    "evidence_quality_assessment",
}

assert required.issubset(set(dependencies))
assert len(dependencies) == len(set(dependencies))

print("AV3_REGISTRY_INTEGRITY_OK")
