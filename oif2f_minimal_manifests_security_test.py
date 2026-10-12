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
from oif.interface.serialization import load_yaml_mapping
for name in NAMES:
    mapping = load_yaml_mapping(MANIFEST_DIR / (name + ".yaml"))
    text = repr(mapping).casefold()
    for token in ("class_path", "entrypoint", "javascript", "file://", "https://"):
        assert token not in text
    assert mapping["operations"] == []
print("OIF2F_SECURITY_OK")
