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
from oif.interface.serialization import load_yaml_mapping, mapping_to_canonical_json
from oif.interface.reference_catalog import ReferenceKind
from oif.interface.reference_resolver import SecureReferenceResolver
# OIF-2C: canonical representation remains deterministic.
for name in NAMES:
    mapping = load_yaml_mapping(MANIFEST_DIR / (name + ".yaml"))
    assert mapping_to_canonical_json(mapping) == mapping_to_canonical_json(mapping)
# OIF-2D: strict five-phase validation remains green.
for name in NAMES:
    report = validator().validate(MANIFEST_DIR / (name + ".yaml"))
    assert report.valid and report.phases_completed == ("parse","schema","semantic","reference","constitution")
# OIF-2E: exact secure resolution remains available without execution.
resolver = SecureReferenceResolver(catalogue())
assert resolver.resolve_exact("nicegui", ReferenceKind.RENDERER).reference_id == "nicegui"
assert resolver.resolve_exact("status_card", ReferenceKind.COMPONENT).reference_id == "status_card"
print("OIF2F_NON_REGRESSION_OK")
