from __future__ import annotations
from dataclasses import FrozenInstanceError
from oif.application.shell_service import ProviderSpec
from oif.interface.reference_catalog import ReferenceCatalogue, ReferenceDescriptor, ReferenceKind
from oif.interface.reference_resolver import ReferenceRequest, SecureReferenceResolver

calls = {"count": 0}
def provider():
    calls["count"] += 1
    return {"status": "ok"}

catalogue = ReferenceCatalogue.from_entries((
    ReferenceDescriptor("runtime-health", ReferenceKind.PROVIDER, "runtime", metadata={"read_only": True}),
    ReferenceDescriptor("refresh", ReferenceKind.OPERATION, "runtime", action_level=0),
    ReferenceDescriptor("status-card", ReferenceKind.COMPONENT, "runtime"),
    ReferenceDescriptor("nicegui", ReferenceKind.RENDERER),
))
resolver = SecureReferenceResolver(catalogue)
resolved = resolver.resolve(ReferenceRequest("runtime-health", ReferenceKind.PROVIDER, "runtime", catalogue.catalogue_sha256))
assert resolved.reference_id == "runtime-health"
assert resolved.kind is ReferenceKind.PROVIDER
assert resolved.zone_id == "runtime"
assert calls["count"] == 0
try:
    resolved.reference_id = "changed"
    raise AssertionError("ResolvedReference must be immutable")
except FrozenInstanceError:
    pass

provider_catalogue = ReferenceCatalogue.from_provider_specs((ProviderSpec("runtime-health", "runtime", provider),))
assert provider_catalogue.ids(ReferenceKind.PROVIDER) == frozenset({"runtime-health"})
assert calls["count"] == 0
snapshot = catalogue.registry_snapshot()
assert "runtime-health" in snapshot.provider_ids
assert "refresh" in snapshot.operation_ids
assert "status-card" in snapshot.component_types
print("OIF2E_FUNCTIONAL_OK")
