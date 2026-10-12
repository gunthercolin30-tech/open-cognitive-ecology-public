from __future__ import annotations
from oif.interface.reference_catalog import ReferenceCatalogue, ReferenceDescriptor, ReferenceKind
from oif.interface.reference_resolver import ReferenceRequest, ReferenceResolutionError, SecureReferenceResolver

catalogue = ReferenceCatalogue.from_entries((ReferenceDescriptor("safe-provider", ReferenceKind.PROVIDER, "runtime"),))
resolver = SecureReferenceResolver(catalogue)
attacks = (
    "package.module:function", "package.module.Class", "__class__", "../secret", "/tmp/provider",
    "file://secret", "https://example.invalid", "safe provider", "safe/provider",
)
for attack in attacks:
    try:
        resolver.resolve(ReferenceRequest(attack, ReferenceKind.PROVIDER))
    except ReferenceResolutionError:
        pass
    else:
        raise AssertionError("unsafe reference accepted: %r" % (attack,))
assert resolver.resolve_exact("safe-provider", ReferenceKind.PROVIDER).reference_id == "safe-provider"
print("OIF2E_SECURITY_OK")
