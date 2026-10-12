from pathlib import Path
from oif.application.default_providers import build_default_provider_specs
from oif.interface.manifest_validator import ManifestValidator, RegistrySnapshot
from oif.interface.reference_catalog import ReferenceCatalogue, ReferenceDescriptor, ReferenceKind

ROOT = Path(__file__).resolve().parent
MANIFEST_DIR = ROOT / "interfaces" / "examples" / "minimal"
NAMES = ("home_minimal", "runtime_health_minimal", "civilizational_state_minimal")

def catalogue():
    providers = ReferenceCatalogue.from_provider_specs(build_default_provider_specs(ROOT)).entries
    extras = (
        ReferenceDescriptor("generic_text", ReferenceKind.COMPONENT),
        ReferenceDescriptor("status_card", ReferenceKind.COMPONENT),
        ReferenceDescriptor("nicegui", ReferenceKind.RENDERER),
    )
    return ReferenceCatalogue.from_entries(tuple(providers) + extras)

def validator():
    return ManifestValidator(registries=catalogue().registry_snapshot())
from oif.interface.serialization import load_json_mapping, load_yaml_mapping, mapping_to_canonical_json, specification_to_json, specification_to_yaml
for name in NAMES:
    y = MANIFEST_DIR / (name + ".yaml")
    j = MANIFEST_DIR / (name + ".json")
    yr = validator().validate(y); jr = validator().validate(j)
    assert yr.valid and jr.valid
    assert yr.manifest.canonical_json() == jr.manifest.canonical_json()
    assert mapping_to_canonical_json(load_yaml_mapping(y)) == mapping_to_canonical_json(load_json_mapping(j))
    y2 = specification_to_yaml(yr.manifest)
    j2 = specification_to_json(yr.manifest)
    assert validator().validate(y2, "yaml").manifest.sha256() == yr.manifest.sha256()
    assert validator().validate(j2, "json").manifest.sha256() == yr.manifest.sha256()
print("OIF2F_ROUND_TRIP_OK")
