"""Immutable allowlisted reference catalogue for OIF-2E.

The catalogue is constructed only by trusted Python composition code. It never
scans the ontology, imports a path supplied by a manifest, executes a provider,
or exposes provider callables to renderers.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional, Tuple

from .models import ModelViolation, freeze_mapping, validate_identifier


class ReferenceCatalogueViolation(ValueError):
    """Raised when trusted catalogue construction violates OIF-2E invariants."""


class ReferenceKind(str, Enum):
    PROVIDER = "provider"
    OPERATION = "operation"
    COMPONENT = "component"
    RENDERER = "renderer"


@dataclass(frozen=True)
class ReferenceDescriptor:
    reference_id: str
    kind: ReferenceKind
    zone_id: Optional[str] = None
    action_level: Optional[int] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "reference_id", validate_identifier(self.reference_id, "reference_id"))
            kind = self.kind if isinstance(self.kind, ReferenceKind) else ReferenceKind(str(self.kind))
            object.__setattr__(self, "kind", kind)
            if self.zone_id is not None:
                object.__setattr__(self, "zone_id", validate_identifier(self.zone_id, "zone_id"))
            if self.action_level is not None:
                if isinstance(self.action_level, bool) or not isinstance(self.action_level, int) or self.action_level < 0:
                    raise ReferenceCatalogueViolation("action_level must be a non-negative integer or None")
            object.__setattr__(self, "metadata", freeze_mapping(self.metadata))
        except (ModelViolation, ValueError) as exc:
            if isinstance(exc, ReferenceCatalogueViolation):
                raise
            raise ReferenceCatalogueViolation(str(exc)) from None

    def canonical_record(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "action_level": self.action_level,
            "kind": self.kind.value,
            "metadata": _thaw(self.metadata),
            "reference_id": self.reference_id,
            "zone_id": self.zone_id,
        })


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class ReferenceCatalogue:
    entries: Tuple[ReferenceDescriptor, ...]
    catalogue_sha256: str = field(init=False)
    _index: Mapping[Tuple[str, str], ReferenceDescriptor] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        entries = tuple(self.entries)
        index = {}
        for entry in entries:
            if not isinstance(entry, ReferenceDescriptor):
                raise ReferenceCatalogueViolation("catalogue entries must be ReferenceDescriptor instances")
            key = (entry.kind.value, entry.reference_id)
            if key in index:
                raise ReferenceCatalogueViolation("duplicate reference: %s:%s" % key)
            index[key] = entry
        ordered = tuple(index[key] for key in sorted(index))
        canonical = [dict(entry.canonical_record()) for entry in ordered]
        payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        object.__setattr__(self, "entries", ordered)
        object.__setattr__(self, "_index", MappingProxyType(dict(index)))
        object.__setattr__(self, "catalogue_sha256", hashlib.sha256(payload).hexdigest())

    @classmethod
    def from_entries(cls, entries: Iterable[ReferenceDescriptor]) -> "ReferenceCatalogue":
        return cls(tuple(entries))

    @classmethod
    def from_provider_specs(cls, provider_specs: Iterable[Any]) -> "ReferenceCatalogue":
        """Create provider descriptors from trusted ProviderSpec objects.

        Only declarative identity is captured. The callable is deliberately not
        retained, inspected, imported, or executed.
        """
        descriptors = []
        for spec in tuple(provider_specs):
            name = getattr(spec, "name", None)
            zone = getattr(spec, "zone", None)
            provider = getattr(spec, "provider", None)
            if provider is None or not callable(provider):
                raise ReferenceCatalogueViolation("ProviderSpec.provider must be callable in trusted composition")
            descriptors.append(ReferenceDescriptor(
                reference_id=name,
                kind=ReferenceKind.PROVIDER,
                zone_id=zone,
                metadata={"read_only": True, "source": "trusted_provider_spec"},
            ))
        return cls(tuple(descriptors))

    def descriptor(self, kind: ReferenceKind, reference_id: str) -> Optional[ReferenceDescriptor]:
        kind_value = kind.value if isinstance(kind, ReferenceKind) else ReferenceKind(str(kind)).value
        return self._index.get((kind_value, reference_id))

    def ids(self, kind: ReferenceKind) -> frozenset[str]:
        kind_value = kind.value if isinstance(kind, ReferenceKind) else ReferenceKind(str(kind)).value
        return frozenset(entry.reference_id for entry in self.entries if entry.kind.value == kind_value)

    def registry_snapshot(self) -> Any:
        """Return an OIF-2D RegistrySnapshot without introducing reverse coupling."""
        from .manifest_validator import RegistrySnapshot
        return RegistrySnapshot.from_values(
            provider_ids=self.ids(ReferenceKind.PROVIDER),
            operation_ids=self.ids(ReferenceKind.OPERATION),
            component_types=self.ids(ReferenceKind.COMPONENT),
            renderer_ids=self.ids(ReferenceKind.RENDERER) or frozenset({"nicegui"}),
        )
