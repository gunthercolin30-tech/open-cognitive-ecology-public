\
from ontology.architecture_registry import ArchitectureRegistry
from ontology.ecology_blueprint import EcologyBlueprint
from ontology.multi_rf_registry import MultiRFRegistry
from ontology.representative_identity_registry import RepresentativeIdentityRegistry


def main() -> None:
    blueprint = EcologyBlueprint().step(inputs={}, persist=False)
    architecture = ArchitectureRegistry().step(inputs={}, persist=False)
    representative = RepresentativeIdentityRegistry().step(
        inputs={},
        persist=False,
    )
    registry = MultiRFRegistry().step(inputs={}, persist=False)

    assert blueprint["ecology_blueprint_status"] == "RF_ECOLOGY_BLUEPRINT_READY"
    assert architecture["primitive"] == "ARCHITECTURE_REGISTRY"
    assert str(representative["primitive"]).lower() == "representative_identity_registry"
    assert registry["primitive"] == "MULTI_RF_REGISTRY"

    assert registry["identity_policy"][
        "rf_identity_distinct_from_architecture_identity"
    ] is True
    assert registry["identity_policy"][
        "rf_identity_distinct_from_representative_identity"
    ] is True

    print("AW1_NON_REGRESSION_OK")


if __name__ == "__main__":
    main()
