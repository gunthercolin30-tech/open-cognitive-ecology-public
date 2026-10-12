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
from oif.interface.manifest_validator import ManifestValidator, RegistrySnapshot
cases = (("runtime_health_minimal", frozenset({"civilizational-state", "validation-report"})), ("civilizational_state_minimal", frozenset({"runtime-health", "validation-report"})))
for name, providers in cases:
    snapshot = RegistrySnapshot.from_values(provider_ids=providers, operation_ids=(), component_types={"generic_text","status_card"}, renderer_ids={"nicegui"})
    report = ManifestValidator(registries=snapshot).validate(MANIFEST_DIR / (name + ".yaml"))
    assert not report.valid
    assert "unknown_provider" in {e.code for e in report.errors}
missing = validator().validate(MANIFEST_DIR / "absent.yaml")
assert not missing.valid and missing.error_count
bad = validator().validate("schema_version: [", "yaml")
assert not bad.valid and bad.error_count
print("OIF2F_DEGRADATION_OK")
