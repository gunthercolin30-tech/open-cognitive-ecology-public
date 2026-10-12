from __future__ import annotations
from oif.interface.reference_catalog import ReferenceCatalogue, ReferenceDescriptor, ReferenceKind
from oif.interface.reference_resolver import ReferenceRequest, SecureReferenceResolver

entries = (
    ReferenceDescriptor("b", ReferenceKind.OPERATION, "runtime", metadata={"z": 2, "a": [1, 2]}),
    ReferenceDescriptor("a", ReferenceKind.PROVIDER, "science", metadata={"read_only": True}),
)
a = ReferenceCatalogue.from_entries(entries)
b = ReferenceCatalogue.from_entries(reversed(entries))
assert a.catalogue_sha256 == b.catalogue_sha256
ra = SecureReferenceResolver(a).resolve(ReferenceRequest("a", ReferenceKind.PROVIDER))
rb = SecureReferenceResolver(b).resolve(ReferenceRequest("a", ReferenceKind.PROVIDER))
assert ra == rb
print("OIF2E_DETERMINISM_OK")
