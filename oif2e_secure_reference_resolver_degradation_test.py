from __future__ import annotations
from oif.interface.reference_catalog import ReferenceCatalogue, ReferenceCatalogueViolation, ReferenceDescriptor, ReferenceKind
from oif.interface.reference_resolver import ReferenceRequest, ReferenceResolutionError, SecureReferenceResolver

def expect(code, fn):
    try:
        fn()
    except ReferenceResolutionError as exc:
        assert exc.code == code, (exc.code, code)
    else:
        raise AssertionError("expected %s" % code)

catalogue = ReferenceCatalogue.from_entries((ReferenceDescriptor("runtime-health", ReferenceKind.PROVIDER, "runtime"),))
resolver = SecureReferenceResolver(catalogue)
expect("unknown_reference", lambda: resolver.resolve(ReferenceRequest("missing", ReferenceKind.PROVIDER)))
expect("unknown_reference", lambda: resolver.resolve(ReferenceRequest("runtime-health", ReferenceKind.OPERATION)))
expect("zone_mismatch", lambda: resolver.resolve(ReferenceRequest("runtime-health", ReferenceKind.PROVIDER, "science")))
expect("catalogue_hash_mismatch", lambda: resolver.resolve(ReferenceRequest("runtime-health", ReferenceKind.PROVIDER, expected_catalogue_sha256="0" * 64)))
try:
    ReferenceCatalogue.from_entries((
        ReferenceDescriptor("x", ReferenceKind.PROVIDER),
        ReferenceDescriptor("x", ReferenceKind.PROVIDER),
    ))
except ReferenceCatalogueViolation:
    pass
else:
    raise AssertionError("duplicate reference accepted")
print("OIF2E_DEGRADATION_OK")
