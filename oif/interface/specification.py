"""Canonical OIF-2B interface specification and cross-reference validation."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .models import (
    AccessibilitySpecification,
    ComponentSpecification,
    DataSourceSpecification,
    InterfaceMetadata,
    LayoutSpecification,
    NavigationSpecification,
    OperationSpecification,
    PermissionSpecification,
    PreferenceSpecification,
)

SCHEMA_VERSION = "oif.interface.v1"


class SpecificationViolation(ValueError):
    pass


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in sorted(value.items())}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {name: _plain(getattr(value, name)) for name in value.__dataclass_fields__}
    if isinstance(value, Enum):
        return value.value
    return value


@dataclass(frozen=True)
class InterfaceSpecification:
    schema_version: str
    interface: InterfaceMetadata
    navigation: NavigationSpecification
    layout: Tuple[LayoutSpecification, ...]
    data_sources: Tuple[DataSourceSpecification, ...]
    components: Tuple[ComponentSpecification, ...]
    operations: Tuple[OperationSpecification, ...]
    permissions: Tuple[PermissionSpecification, ...]
    preferences: Tuple[PreferenceSpecification, ...]
    accessibility: AccessibilitySpecification

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise SpecificationViolation("unsupported schema_version: %r" % self.schema_version)
        for name in ("layout", "data_sources", "components", "operations", "permissions", "preferences"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        self._validate()

    def _validate(self) -> None:
        layout_ids = _unique_map("layout_id", self.layout)
        provider_ids = _unique_map("provider_id", self.data_sources)
        component_ids = _unique_map("component_id", self.components)
        operation_ids = _unique_map("operation_id", self.operations)
        permission_ids = _unique_map("permission_id", self.permissions)
        _unique_map("preference_id", self.preferences)
        zone_ids = {zone.zone_id for zone in self.navigation.zones}

        for zone in self.navigation.zones:
            if zone.layout_id not in layout_ids:
                raise SpecificationViolation("zone %s references unknown layout %s" % (zone.zone_id, zone.layout_id))
        for source in self.data_sources:
            if source.zone_id not in zone_ids:
                raise SpecificationViolation("provider %s references unknown zone %s" % (source.provider_id, source.zone_id))
        for layout in self.layout:
            for region in layout.regions:
                for component_id in region.component_ids:
                    if component_id not in component_ids:
                        raise SpecificationViolation("region %s references unknown component %s" % (region.region_id, component_id))
        for component in self.components:
            if component.provider_id is not None and component.provider_id not in provider_ids:
                raise SpecificationViolation("component %s references unknown provider %s" % (component.component_id, component.provider_id))
            for operation_id in component.operation_ids:
                if operation_id not in operation_ids:
                    raise SpecificationViolation("component %s references unknown operation %s" % (component.component_id, operation_id))
        for operation in self.operations:
            for permission_id in operation.permission_ids:
                if permission_id not in permission_ids:
                    raise SpecificationViolation("operation %s references unknown permission %s" % (operation.operation_id, permission_id))

    def as_dict(self) -> Mapping[str, Any]:
        return MappingProxyType(_plain(self))

    def canonical_json(self) -> str:
        return json.dumps(_plain(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def _unique_map(attribute: str, values: Any) -> Mapping[str, Any]:
    result = {}
    for value in values:
        key = getattr(value, attribute)
        if key in result:
            raise SpecificationViolation("duplicate %s: %s" % (attribute, key))
        result[key] = value
    return MappingProxyType(result)
