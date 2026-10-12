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
import sys
from dataclasses import FrozenInstanceError
from oif.interface.abstract_renderer import render_abstract
before = set(sys.modules)
for name in NAMES:
    report = validator().validate(MANIFEST_DIR / (name + ".yaml")); assert report.valid
    a = render_abstract(report.manifest); b = render_abstract(report.manifest)
    assert a == b
    assert tuple(z.order for z in a.zones) == tuple(sorted(z.order for z in a.zones))
    try:
        a.title = "tamper"
        raise AssertionError("tree mutable")
    except FrozenInstanceError:
        pass
assert "nicegui" not in (set(sys.modules) - before)
print("OIF2F_ABSTRACT_RENDER_OK")
