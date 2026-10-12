from pathlib import Path
from oif.application.default_providers import build_default_provider_specs
from oif.interface.manifest_validator import ManifestValidator
from oif.interface.reference_catalog import ReferenceCatalogue, ReferenceDescriptor, ReferenceKind
ROOT=Path(__file__).resolve().parent
MANIFEST_DIR=ROOT/"interfaces"/"examples"/"complex"
NAMES=("portal_pilot","civilizational_state_pilot","science_validation_pilot")
def catalogue(missing=()):
    providers=[e for e in ReferenceCatalogue.from_provider_specs(build_default_provider_specs(ROOT)).entries if e.reference_id not in set(missing)]
    extras=(ReferenceDescriptor("generic_text",ReferenceKind.COMPONENT),ReferenceDescriptor("status_card",ReferenceKind.COMPONENT),ReferenceDescriptor("nicegui",ReferenceKind.RENDERER))
    return ReferenceCatalogue.from_entries(tuple(providers)+extras)
def validator(missing=()): return ManifestValidator(registries=catalogue(missing).registry_snapshot())
