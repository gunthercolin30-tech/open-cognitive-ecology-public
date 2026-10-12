"""Immutable declarative models for the OIF-2B canonical manifest.

This module is renderer-independent and performs no dynamic import, execution,
persistence, networking, or governance action.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from oif_functional_constitution import ActionLevel

IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
FORBIDDEN_DECLARATIVE_KEYS = frozenset({
    "module", "class_path", "callable", "entrypoint", "python",
    "javascript", "shell", "eval", "exec", "import",
})


class ModelViolation(ValueError):
    pass


def validate_identifier(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ModelViolation("%s must be a string" % field_name)
    candidate = value.strip()
    if not IDENTIFIER_PATTERN.fullmatch(candidate):
        raise ModelViolation("invalid %s: %r" % (field_name, value))
    return candidate


def validate_text(value: str, field_name: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ModelViolation("%s must be a string" % field_name)
    candidate = value.strip()
    if not allow_empty and not candidate:
        raise ModelViolation("%s must not be empty" % field_name)
    return candidate


def _freeze(value: Any, depth: int = 0) -> Any:
    if depth > 32:
        raise ModelViolation("maximum declarative nesting depth exceeded")
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, tuple):
        return tuple(_freeze(item, depth + 1) for item in value)
    if isinstance(value, list):
        return tuple(_freeze(item, depth + 1) for item in value)
    if isinstance(value, (set, frozenset)):
        frozen_items = tuple(_freeze(item, depth + 1) for item in value)
        return tuple(sorted(frozen_items, key=repr))
    if isinstance(value, Mapping):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ModelViolation("declarative mapping keys must be strings")
            normalized_key = key.strip()
            if not normalized_key:
                raise ModelViolation("declarative mapping keys must not be empty")
            if normalized_key.casefold() in FORBIDDEN_DECLARATIVE_KEYS:
                raise ModelViolation("forbidden declarative key: %s" % normalized_key)
            result[normalized_key] = _freeze(item, depth + 1)
        return MappingProxyType(dict(sorted(result.items())))
    raise ModelViolation("unsupported declarative value type: %s" % type(value).__name__)


def freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ModelViolation("expected mapping")
    frozen = _freeze(value)
    if not isinstance(frozen, Mapping):
        raise ModelViolation("expected frozen mapping")
    return frozen


def _unique(label: str, values: Any) -> None:
    sequence = tuple(values)
    if len(sequence) != len(set(sequence)):
        raise ModelViolation("duplicate %s" % label)


@dataclass(frozen=True)
class InterfaceMetadata:
    interface_id: str
    title: str
    renderer_id: str
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "interface_id", validate_identifier(self.interface_id, "interface_id"))
        object.__setattr__(self, "renderer_id", validate_identifier(self.renderer_id, "renderer_id"))
        object.__setattr__(self, "title", validate_text(self.title, "title"))
        object.__setattr__(self, "description", validate_text(self.description, "description", True))
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))


@dataclass(frozen=True)
class NavigationZoneSpecification:
    zone_id: str
    label: str
    description: str
    order: int
    layout_id: str
    access_mode: str = "read_only"

    def __post_init__(self) -> None:
        object.__setattr__(self, "zone_id", validate_identifier(self.zone_id, "zone_id"))
        object.__setattr__(self, "layout_id", validate_identifier(self.layout_id, "layout_id"))
        object.__setattr__(self, "label", validate_text(self.label, "label"))
        object.__setattr__(self, "description", validate_text(self.description, "description", True))
        object.__setattr__(self, "access_mode", validate_identifier(self.access_mode, "access_mode"))
        if not isinstance(self.order, int) or isinstance(self.order, bool) or self.order < 0:
            raise ModelViolation("order must be a non-negative integer")


@dataclass(frozen=True)
class NavigationSpecification:
    default_zone_id: str
    zones: Tuple[NavigationZoneSpecification, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "default_zone_id", validate_identifier(self.default_zone_id, "default_zone_id"))
        object.__setattr__(self, "zones", tuple(self.zones))
        _unique("zone_id", (zone.zone_id for zone in self.zones))
        orders = tuple(zone.order for zone in self.zones)
        if len(orders) != len(set(orders)):
            raise ModelViolation("navigation orders must be unique")
        if self.default_zone_id not in {zone.zone_id for zone in self.zones}:
            raise ModelViolation("default_zone_id must reference a declared zone")


@dataclass(frozen=True)
class LayoutRegionSpecification:
    region_id: str
    component_ids: Tuple[str, ...]
    order: int = 0
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "region_id", validate_identifier(self.region_id, "region_id"))
        object.__setattr__(self, "component_ids", tuple(validate_identifier(x, "component_id") for x in self.component_ids))
        _unique("component_id", self.component_ids)
        if not isinstance(self.order, int) or isinstance(self.order, bool) or self.order < 0:
            raise ModelViolation("region order must be a non-negative integer")
        object.__setattr__(self, "properties", freeze_mapping(self.properties))


@dataclass(frozen=True)
class LayoutSpecification:
    layout_id: str
    regions: Tuple[LayoutRegionSpecification, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "layout_id", validate_identifier(self.layout_id, "layout_id"))
        object.__setattr__(self, "regions", tuple(self.regions))
        _unique("region_id", (region.region_id for region in self.regions))


@dataclass(frozen=True)
class DataSourceSpecification:
    provider_id: str
    zone_id: str
    data_contract: str
    required: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider_id", validate_identifier(self.provider_id, "provider_id"))
        object.__setattr__(self, "zone_id", validate_identifier(self.zone_id, "zone_id"))
        object.__setattr__(self, "data_contract", validate_identifier(self.data_contract, "data_contract"))
        if not isinstance(self.required, bool):
            raise ModelViolation("required must be boolean")
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))


@dataclass(frozen=True)
class ComponentSpecification:
    component_id: str
    component_type: str
    provider_id: Optional[str] = None
    operation_ids: Tuple[str, ...] = ()
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "component_id", validate_identifier(self.component_id, "component_id"))
        object.__setattr__(self, "component_type", validate_identifier(self.component_type, "component_type"))
        if self.provider_id is not None:
            object.__setattr__(self, "provider_id", validate_identifier(self.provider_id, "provider_id"))
        object.__setattr__(self, "operation_ids", tuple(validate_identifier(x, "operation_id") for x in self.operation_ids))
        _unique("operation_id", self.operation_ids)
        object.__setattr__(self, "properties", freeze_mapping(self.properties))


@dataclass(frozen=True)
class PermissionSpecification:
    permission_id: str
    description: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "permission_id", validate_identifier(self.permission_id, "permission_id"))
        object.__setattr__(self, "description", validate_text(self.description, "description"))


@dataclass(frozen=True)
class OperationSpecification:
    operation_id: str
    action_level: ActionLevel
    permission_ids: Tuple[str, ...]
    governance_route: Tuple[str, ...] = ()
    confirmation_required: bool = False
    journal_required: bool = False
    rollback_strategy: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "operation_id", validate_identifier(self.operation_id, "operation_id"))
        if not isinstance(self.action_level, ActionLevel):
            try:
                object.__setattr__(self, "action_level", ActionLevel(int(self.action_level)))
            except Exception:
                raise ModelViolation("invalid action_level")
        object.__setattr__(self, "permission_ids", tuple(validate_identifier(x, "permission_id") for x in self.permission_ids))
        _unique("permission_id", self.permission_ids)
        object.__setattr__(self, "governance_route", tuple(validate_identifier(x, "governance_route item") for x in self.governance_route))
        if not isinstance(self.confirmation_required, bool):
            raise ModelViolation("confirmation_required must be boolean")
        if not isinstance(self.journal_required, bool):
            raise ModelViolation("journal_required must be boolean")
        if self.rollback_strategy is not None:
            object.__setattr__(self, "rollback_strategy", validate_identifier(self.rollback_strategy, "rollback_strategy"))
        if self.action_level >= ActionLevel.GOVERNED_WRITE:
            if not self.permission_ids:
                raise ModelViolation("governed operations require permissions")
            if not self.confirmation_required:
                raise ModelViolation("governed operations require confirmation")
            if not self.journal_required:
                raise ModelViolation("governed operations require journaling")
            if not self.governance_route:
                raise ModelViolation("governed operations require governance_route")


@dataclass(frozen=True)
class PreferenceSpecification:
    preference_id: str
    value_type: str
    default_value: Any
    allowed_values: Tuple[Any, ...] = ()
    renderer_local: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "preference_id", validate_identifier(self.preference_id, "preference_id"))
        object.__setattr__(self, "value_type", validate_identifier(self.value_type, "value_type"))
        object.__setattr__(self, "default_value", _freeze(self.default_value))
        object.__setattr__(self, "allowed_values", tuple(_freeze(x) for x in self.allowed_values))
        if not isinstance(self.renderer_local, bool):
            raise ModelViolation("renderer_local must be boolean")
        if self.allowed_values and self.default_value not in self.allowed_values:
            raise ModelViolation("default_value must belong to allowed_values")


@dataclass(frozen=True)
class AccessibilitySpecification:
    language: str = "fr"
    keyboard_navigation: bool = True
    screen_reader_labels: bool = True
    reduced_motion_supported: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "language", validate_identifier(self.language, "language"))
        for name in ("keyboard_navigation", "screen_reader_labels", "reduced_motion_supported"):
            if not isinstance(getattr(self, name), bool):
                raise ModelViolation("%s must be boolean" % name)
        object.__setattr__(self, "metadata", freeze_mapping(self.metadata))
