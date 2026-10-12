"""Strict renderer-independent OIF-2D manifest validator.

Pipeline: parse -> schema -> semantic -> reference -> constitution.
The validator is side-effect free and never imports or executes code declared by a
manifest. NiceGUI is intentionally not imported here.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple, Union

from jsonschema import Draft202012Validator

from oif.schemas import OIF_INTERFACE_SCHEMA_V1
from oif_functional_constitution import ActionLevel, REQUIRED_GOVERNANCE_DEPENDENCIES

from .models import (
    AccessibilitySpecification,
    ComponentSpecification,
    DataSourceSpecification,
    InterfaceMetadata,
    LayoutRegionSpecification,
    LayoutSpecification,
    ModelViolation,
    NavigationSpecification,
    NavigationZoneSpecification,
    OperationSpecification,
    PermissionSpecification,
    PreferenceSpecification,
)
from .serialization import SerializationViolation, load_json_mapping, load_yaml_mapping
from .specification import InterfaceSpecification, SpecificationViolation
from .validation_errors import ManifestValidationError, ManifestValidationReport

PHASES = ("parse", "schema", "semantic", "reference", "constitution")
DEFAULT_ALLOWED_ZONES = frozenset({
    "overview", "runtime", "experiments", "science", "memory",
    "governance", "system",
})
DEFAULT_RENDERERS = frozenset({"nicegui"})
EXECUTABLE_KEY = re.compile(
    r"^(module|class_path|callable|entrypoint|python|javascript|shell|eval|exec|import|script|command)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RegistrySnapshot:
    provider_ids: Optional[frozenset[str]] = None
    operation_ids: Optional[frozenset[str]] = None
    component_types: Optional[frozenset[str]] = None
    renderer_ids: frozenset[str] = DEFAULT_RENDERERS
    zone_ids: frozenset[str] = DEFAULT_ALLOWED_ZONES

    @classmethod
    def from_values(
        cls,
        provider_ids: Optional[Iterable[str]] = None,
        operation_ids: Optional[Iterable[str]] = None,
        component_types: Optional[Iterable[str]] = None,
        renderer_ids: Iterable[str] = DEFAULT_RENDERERS,
        zone_ids: Iterable[str] = DEFAULT_ALLOWED_ZONES,
    ) -> "RegistrySnapshot":
        def frozen(values: Optional[Iterable[str]]) -> Optional[frozenset[str]]:
            return None if values is None else frozenset(str(v) for v in values)
        return cls(
            provider_ids=frozen(provider_ids),
            operation_ids=frozen(operation_ids),
            component_types=frozen(component_types),
            renderer_ids=frozenset(str(v) for v in renderer_ids),
            zone_ids=frozenset(str(v) for v in zone_ids),
        )


class ManifestValidator:
    def __init__(
        self,
        registries: Optional[RegistrySnapshot] = None,
        schema_path: Path = OIF_INTERFACE_SCHEMA_V1,
        max_errors: int = 128,
    ) -> None:
        if not isinstance(max_errors, int) or isinstance(max_errors, bool) or max_errors < 1:
            raise ValueError("max_errors must be a positive integer")
        self._registries = registries or RegistrySnapshot()
        self._schema_path = Path(schema_path)
        self._max_errors = max_errors

    def validate(
        self,
        source: Union[str, Path, Mapping[str, Any]],
        source_format: Optional[str] = None,
    ) -> ManifestValidationReport:
        errors: list[ManifestValidationError] = []
        completed: list[str] = []
        mapping: Optional[Mapping[str, Any]] = None
        specification: Optional[InterfaceSpecification] = None

        mapping, parse_errors = self._parse(source, source_format)
        errors.extend(parse_errors)
        completed.append("parse")
        if mapping is None:
            return self._report(None, errors, completed)

        errors.extend(self._schema(mapping))
        completed.append("schema")
        errors.extend(self._security_scan(mapping))

        specification, semantic_errors = self._semantic(mapping)
        errors.extend(semantic_errors)
        completed.append("semantic")

        errors.extend(self._references(mapping))
        completed.append("reference")

        errors.extend(self._constitution(mapping, specification))
        completed.append("constitution")
        return self._report(specification, errors, completed)

    def _report(
        self,
        specification: Optional[InterfaceSpecification],
        errors: Sequence[ManifestValidationError],
        completed: Sequence[str],
    ) -> ManifestValidationReport:
        unique = {(e.phase, e.code, e.path, e.message, e.suggestion): e for e in errors}
        ordered = tuple(sorted(unique.values())[: self._max_errors])
        return ManifestValidationReport(
            valid=not ordered,
            manifest=specification if not ordered else None,
            errors=ordered,
            phases_completed=tuple(completed),
        )

    def _parse(
        self,
        source: Union[str, Path, Mapping[str, Any]],
        source_format: Optional[str],
    ) -> tuple[Optional[Mapping[str, Any]], list[ManifestValidationError]]:
        if isinstance(source, Mapping):
            try:
                text = json.dumps(source, ensure_ascii=False, allow_nan=False)
                return load_json_mapping(text), []
            except (TypeError, ValueError, SerializationViolation):
                return None, [self._error("parse", "invalid_mapping", "/", "Manifest mapping is not a safe JSON-compatible object.", "Use only finite JSON values and string keys.")]
        fmt = (source_format or "").strip().lower()
        if not fmt and isinstance(source, Path):
            fmt = source.suffix.lower().lstrip(".")
        if not fmt:
            fmt = "json"
        try:
            if fmt in {"yaml", "yml"}:
                return load_yaml_mapping(source), []
            if fmt == "json":
                return load_json_mapping(source), []
            return None, [self._error("parse", "unsupported_format", "/", "Manifest format is not supported.", "Use JSON or YAML.")]
        except (SerializationViolation, UnicodeError, OSError):
            return None, [self._error("parse", "invalid_document", "/", "Manifest could not be parsed safely.", "Check syntax, encoding, size, and document root type.")]

    def _schema(self, mapping: Mapping[str, Any]) -> list[ManifestValidationError]:
        try:
            schema = json.loads(self._schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
        except (OSError, UnicodeError, json.JSONDecodeError, Exception) as exc:
            # The exception object is intentionally not exposed in the diagnostic.
            del exc
            return [self._error("schema", "schema_unavailable", "/", "Canonical schema is unavailable or invalid.", "Restore the certified OIF-2C schema before validation.")]
        result: list[ManifestValidationError] = []
        for violation in sorted(validator.iter_errors(mapping), key=lambda e: (tuple(str(p) for p in e.absolute_path), e.validator or "", e.message)):
            path = self._json_pointer(tuple(violation.absolute_path))
            code = "schema_" + str(violation.validator or "violation")
            result.append(self._error("schema", code, path, "Manifest does not satisfy the canonical schema.", "Correct the value at the indicated path according to OIF schema v1."))
        return result

    def _semantic(self, mapping: Mapping[str, Any]) -> tuple[Optional[InterfaceSpecification], list[ManifestValidationError]]:
        try:
            return self._build_specification(mapping), []
        except (KeyError, TypeError, ValueError, ModelViolation, SpecificationViolation):
            return None, [self._error("semantic", "canonical_model_rejected", "/", "Manifest violates canonical model invariants.", "Correct identifiers, uniqueness constraints, and internal references.")]

    def _references(self, mapping: Mapping[str, Any]) -> list[ManifestValidationError]:
        errors: list[ManifestValidationError] = []
        registries = self._registries
        interface = mapping.get("interface")
        if isinstance(interface, Mapping):
            renderer_id = interface.get("renderer_id")
            if isinstance(renderer_id, str) and renderer_id not in registries.renderer_ids:
                errors.append(self._error("reference", "unknown_renderer", "/interface/renderer_id", "Renderer is not registered.", "Select a renderer from the renderer registry."))
        navigation = mapping.get("navigation")
        if isinstance(navigation, Mapping):
            zones = navigation.get("zones")
            if isinstance(zones, list):
                for index, zone in enumerate(zones):
                    if isinstance(zone, Mapping):
                        zone_id = zone.get("zone_id")
                        if isinstance(zone_id, str) and zone_id not in registries.zone_ids:
                            errors.append(self._error("reference", "unknown_zone", f"/navigation/zones/{index}/zone_id", "Zone is not allowed by the OIF blueprint.", "Select a canonical OIF zone."))
        data_sources = mapping.get("data_sources")
        if registries.provider_ids is not None and isinstance(data_sources, list):
            for index, source in enumerate(data_sources):
                if isinstance(source, Mapping):
                    provider_id = source.get("provider_id")
                    if isinstance(provider_id, str) and provider_id not in registries.provider_ids:
                        errors.append(self._error("reference", "unknown_provider", f"/data_sources/{index}/provider_id", "Provider is not registered.", "Select a provider from the provider registry."))
        components = mapping.get("components")
        if isinstance(components, list):
            for index, component in enumerate(components):
                if not isinstance(component, Mapping):
                    continue
                component_type = component.get("component_type")
                if registries.component_types is not None and isinstance(component_type, str) and component_type not in registries.component_types:
                    errors.append(self._error("reference", "unknown_component", f"/components/{index}/component_type", "Component type is not registered.", "Select a component from the component catalogue."))
                operation_ids = component.get("operation_ids")
                if registries.operation_ids is not None and isinstance(operation_ids, list):
                    for op_index, operation_id in enumerate(operation_ids):
                        if isinstance(operation_id, str) and operation_id not in registries.operation_ids:
                            errors.append(self._error("reference", "unknown_operation", f"/components/{index}/operation_ids/{op_index}", "Operation is not registered.", "Select an operation from the governed operation registry."))
        return errors

    def _constitution(
        self,
        mapping: Mapping[str, Any],
        specification: Optional[InterfaceSpecification],
    ) -> list[ManifestValidationError]:
        errors: list[ManifestValidationError] = []
        operations = mapping.get("operations")
        if isinstance(operations, list):
            required_route = tuple(REQUIRED_GOVERNANCE_DEPENDENCIES)
            for index, operation in enumerate(operations):
                if not isinstance(operation, Mapping):
                    continue
                level = operation.get("action_level")
                try:
                    action_level = ActionLevel(int(level))
                except (TypeError, ValueError):
                    continue
                if action_level >= ActionLevel.GOVERNED_WRITE:
                    route = operation.get("governance_route")
                    route_values = set(route) if isinstance(route, list) else set()
                    missing = [item for item in required_route if item not in route_values]
                    if missing:
                        errors.append(self._error("constitution", "governance_route_incomplete", f"/operations/{index}/governance_route", "Governed operation lacks required governance dependencies.", "Declare the complete constitutional governance route."))
                    if operation.get("confirmation_required") is not True:
                        errors.append(self._error("constitution", "confirmation_required", f"/operations/{index}/confirmation_required", "Governed operation requires explicit confirmation.", "Set confirmation_required to true."))
                    if operation.get("journal_required") is not True:
                        errors.append(self._error("constitution", "journal_required", f"/operations/{index}/journal_required", "Governed operation requires audit journaling.", "Set journal_required to true."))
                    permissions = operation.get("permission_ids")
                    if not isinstance(permissions, list) or not permissions:
                        errors.append(self._error("constitution", "permissions_required", f"/operations/{index}/permission_ids", "Governed operation requires permissions.", "Declare at least one governed permission."))
        if specification is not None:
            metadata = specification.interface.metadata
            if metadata.get("consciousness_proven") is True or metadata.get("subjectivity_proven") is True or metadata.get("qualia_proven") is True or metadata.get("phenomenology_proven") is True:
                errors.append(self._error("constitution", "epistemic_overclaim", "/interface/metadata", "Manifest asserts an unverified phenomenal property.", "Use functional conclusions only and keep phenomenology undetermined."))
        return errors

    def _security_scan(self, value: Any, path: tuple[Any, ...] = ()) -> list[ManifestValidationError]:
        errors: list[ManifestValidationError] = []
        if isinstance(value, Mapping):
            for key in sorted(value, key=str):
                child_path = path + (key,)
                if isinstance(key, str) and EXECUTABLE_KEY.fullmatch(key.strip()):
                    errors.append(self._error("schema", "arbitrary_code_field", self._json_pointer(child_path), "Executable declaration fields are forbidden.", "Use registered declarative providers, components, and operations only."))
                errors.extend(self._security_scan(value[key], child_path))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                errors.extend(self._security_scan(item, path + (index,)))
        return errors

    @staticmethod
    def _build_specification(mapping: Mapping[str, Any]) -> InterfaceSpecification:
        interface = mapping["interface"]
        navigation = mapping["navigation"]
        return InterfaceSpecification(
            schema_version=mapping["schema_version"],
            interface=InterfaceMetadata(**interface),
            navigation=NavigationSpecification(
                default_zone_id=navigation["default_zone_id"],
                zones=tuple(NavigationZoneSpecification(**zone) for zone in navigation["zones"]),
            ),
            layout=tuple(LayoutSpecification(
                layout_id=layout["layout_id"],
                regions=tuple(LayoutRegionSpecification(**region) for region in layout["regions"]),
            ) for layout in mapping["layout"]),
            data_sources=tuple(DataSourceSpecification(**source) for source in mapping["data_sources"]),
            components=tuple(ComponentSpecification(**component) for component in mapping["components"]),
            operations=tuple(OperationSpecification(**operation) for operation in mapping["operations"]),
            permissions=tuple(PermissionSpecification(**permission) for permission in mapping["permissions"]),
            preferences=tuple(PreferenceSpecification(**preference) for preference in mapping["preferences"]),
            accessibility=AccessibilitySpecification(**mapping["accessibility"]),
        )

    @staticmethod
    def _json_pointer(parts: Sequence[Any]) -> str:
        if not parts:
            return "/"
        encoded = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
        return "/" + "/".join(encoded)

    @staticmethod
    def _error(phase: str, code: str, path: str, message: str, suggestion: str) -> ManifestValidationError:
        return ManifestValidationError(phase, code, path, message, suggestion)


def validate_manifest(
    source: Union[str, Path, Mapping[str, Any]],
    source_format: Optional[str] = None,
    registries: Optional[RegistrySnapshot] = None,
    max_errors: int = 128,
) -> ManifestValidationReport:
    return ManifestValidator(registries=registries, max_errors=max_errors).validate(source, source_format)
