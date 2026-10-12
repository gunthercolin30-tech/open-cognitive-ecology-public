"""Canonical renderer-independent OIF interface specification."""
from .manifest_validator import ManifestValidator, RegistrySnapshot, validate_manifest
from .models import (
    AccessibilitySpecification,
    ComponentSpecification,
    DataSourceSpecification,
    InterfaceMetadata,
    LayoutRegionSpecification,
    LayoutSpecification,
    NavigationSpecification,
    NavigationZoneSpecification,
    OperationSpecification,
    PermissionSpecification,
    PreferenceSpecification,
)
from .specification import InterfaceSpecification, SpecificationViolation
from .validation_errors import ManifestValidationError, ManifestValidationReport

__all__ = (
    "AccessibilitySpecification",
    "ComponentSpecification",
    "DataSourceSpecification",
    "InterfaceMetadata",
    "InterfaceSpecification",
    "LayoutRegionSpecification",
    "LayoutSpecification",
    "ManifestValidationError",
    "ManifestValidationReport",
    "ManifestValidator",
    "NavigationSpecification",
    "NavigationZoneSpecification",
    "OperationSpecification",
    "PermissionSpecification",
    "PreferenceSpecification",
    "RegistrySnapshot",
    "SpecificationViolation",
    "validate_manifest",
    "ReferenceCatalogue",
    "ReferenceCatalogueViolation",
    "ReferenceDescriptor",
    "ReferenceKind",
    "ReferenceRequest",
    "ReferenceResolutionError",
    "ResolvedReference",
    "SecureReferenceResolver",
)

# OIF-2E secure reference resolution public API.
from .reference_catalog import (
    ReferenceCatalogue,
    ReferenceCatalogueViolation,
    ReferenceDescriptor,
    ReferenceKind,
)
from .reference_resolver import (
    ReferenceRequest,
    ReferenceResolutionError,
    ResolvedReference,
    SecureReferenceResolver,
)
