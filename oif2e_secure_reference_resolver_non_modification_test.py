from __future__ import annotations
import hashlib
from pathlib import Path
from oif.interface.reference_catalog import ReferenceCatalogue, ReferenceDescriptor, ReferenceKind
from oif.interface.reference_resolver import SecureReferenceResolver

ROOT = Path.home() / "open-cognitive-ecology"
targets = (
    "oif/interface/models.py", "oif/interface/specification.py", "oif/interface/manifest_validator.py",
    "oif/schemas/oif_interface_schema_v1.json", "oif/application/default_providers.py", "oif/application/shell_service.py",
)
before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in targets}
catalogue = ReferenceCatalogue.from_entries((ReferenceDescriptor("runtime-health", ReferenceKind.PROVIDER, "runtime"),))
SecureReferenceResolver(catalogue)
after = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in targets}
assert before == after
print("OIF2E_NON_MODIFICATION_OK")
