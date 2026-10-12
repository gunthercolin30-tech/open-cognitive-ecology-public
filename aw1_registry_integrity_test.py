\
from dependency_registry import DEPENDENCY_REGISTRY
from ontology_inventory import ONTOLOGY_INVENTORY as ROOT_INVENTORY
from ontology.ontology_inventory import ONTOLOGY_INVENTORY as PACKAGE_INVENTORY


def main() -> None:
    assert ROOT_INVENTORY.count("multi_rf_registry") == 1
    assert PACKAGE_INVENTORY.count("multi_rf_registry") == 1
    assert "multi_rf_registry" in DEPENDENCY_REGISTRY

    dependencies = DEPENDENCY_REGISTRY["multi_rf_registry"]
    required = {
        "ecology_blueprint",
        "architecture_registry",
        "representative_identity_registry",
        "representative_lineage_registry",
        "distributed_population_runtime",
        "individual_lifecycle_management",
        "civilizational_state_persistence",
        "identity_continuity_index",
        "ontology_redundancy_audit",
        "ontological_non_duplication_checker",
        "collective_naming_protocol",
        "epistemic_guard",
    }
    assert required.issubset(set(dependencies))
    assert len(dependencies) == len(set(dependencies))

    print("AW1_REGISTRY_INTEGRITY_OK")


if __name__ == "__main__":
    main()
