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
from oif.interface.abstract_renderer import render_abstract
from oif.interface.reference_resolver import SecureReferenceResolver
for name in NAMES:
    report = validator().validate(MANIFEST_DIR / (name + ".yaml"))
    assert report.valid, (name, [e.code for e in report.errors])
    spec = report.manifest
    assert not spec.operations and not spec.permissions
    tree = render_abstract(spec)
    assert tree.interface_id == spec.interface.interface_id
    assert tree.source_sha256 == spec.sha256()
resolver = SecureReferenceResolver(catalogue())
resolver.resolve_exact("runtime-health", __import__('oif.interface.reference_catalog', fromlist=['ReferenceKind']).ReferenceKind.PROVIDER, "runtime")
resolver.resolve_exact("civilizational-state", __import__('oif.interface.reference_catalog', fromlist=['ReferenceKind']).ReferenceKind.PROVIDER, "memory")
print("OIF2F_FUNCTIONAL_OK")
