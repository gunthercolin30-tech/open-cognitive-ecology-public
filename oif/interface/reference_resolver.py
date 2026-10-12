"""Side-effect-free secure reference resolver for OIF-2E."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .models import ModelViolation, validate_identifier
from .reference_catalog import ReferenceCatalogue, ReferenceDescriptor, ReferenceKind


class ReferenceResolutionError(LookupError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


_FORBIDDEN_REFERENCE = re.compile(
    r"(?:^|[./:\\])(?:__[^/.:\\]+__|\.\.?)(?:$|[./:\\])|"
    r"(?:^|[^a-z])(file|https?|ftp|data|javascript)://|"
    r"[\\/]|:|\s",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReferenceRequest:
    reference_id: str
    expected_kind: ReferenceKind
    expected_zone_id: Optional[str] = None
    expected_catalogue_sha256: Optional[str] = None

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "reference_id", validate_identifier(self.reference_id, "reference_id"))
        except ModelViolation as exc:
            raise ReferenceResolutionError("unsafe_reference", "Reference identifier is not a canonical OIF identifier.") from None
        try:
            kind = self.expected_kind if isinstance(self.expected_kind, ReferenceKind) else ReferenceKind(str(self.expected_kind))
        except ValueError:
            raise ReferenceResolutionError("invalid_kind", "Reference kind is not supported.") from None
        object.__setattr__(self, "expected_kind", kind)
        if self.expected_zone_id is not None:
            try:
                object.__setattr__(self, "expected_zone_id", validate_identifier(self.expected_zone_id, "expected_zone_id"))
            except ModelViolation:
                raise ReferenceResolutionError("invalid_zone", "Expected zone is not a canonical OIF identifier.") from None
        if self.expected_catalogue_sha256 is not None:
            value = self.expected_catalogue_sha256
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ReferenceResolutionError("invalid_catalogue_hash", "Expected catalogue hash must be lowercase SHA-256.")


@dataclass(frozen=True)
class ResolvedReference:
    reference_id: str
    kind: ReferenceKind
    zone_id: Optional[str]
    action_level: Optional[int]
    metadata: object
    catalogue_sha256: str

    @classmethod
    def from_descriptor(cls, descriptor: ReferenceDescriptor, catalogue_sha256: str) -> "ResolvedReference":
        return cls(
            reference_id=descriptor.reference_id,
            kind=descriptor.kind,
            zone_id=descriptor.zone_id,
            action_level=descriptor.action_level,
            metadata=descriptor.metadata,
            catalogue_sha256=catalogue_sha256,
        )


class SecureReferenceResolver:
    """Resolve only exact allowlisted catalogue entries.

    Resolution performs no provider call, import, file access, networking,
    persistence, UI rendering, alias expansion, or ontology scanning.
    """

    def __init__(self, catalogue: ReferenceCatalogue) -> None:
        if not isinstance(catalogue, ReferenceCatalogue):
            raise TypeError("catalogue must be a ReferenceCatalogue")
        self._catalogue = catalogue

    @property
    def catalogue_sha256(self) -> str:
        return self._catalogue.catalogue_sha256

    def resolve(self, request: ReferenceRequest) -> ResolvedReference:
        if not isinstance(request, ReferenceRequest):
            raise TypeError("request must be a ReferenceRequest")
        if _FORBIDDEN_REFERENCE.search(request.reference_id):
            raise ReferenceResolutionError("unsafe_reference", "Reference identifier contains a forbidden form.")
        if request.expected_catalogue_sha256 is not None and request.expected_catalogue_sha256 != self.catalogue_sha256:
            raise ReferenceResolutionError("catalogue_hash_mismatch", "Reference catalogue differs from the expected immutable snapshot.")
        descriptor = self._catalogue.descriptor(request.expected_kind, request.reference_id)
        if descriptor is None:
            raise ReferenceResolutionError("unknown_reference", "Reference is not present in the allowlisted catalogue.")
        if request.expected_zone_id is not None and descriptor.zone_id != request.expected_zone_id:
            raise ReferenceResolutionError("zone_mismatch", "Resolved reference does not belong to the expected zone.")
        return ResolvedReference.from_descriptor(descriptor, self.catalogue_sha256)

    def resolve_exact(
        self,
        reference_id: str,
        expected_kind: ReferenceKind,
        expected_zone_id: Optional[str] = None,
    ) -> ResolvedReference:
        return self.resolve(ReferenceRequest(reference_id, expected_kind, expected_zone_id, self.catalogue_sha256))
