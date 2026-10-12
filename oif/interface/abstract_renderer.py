"""Pure immutable abstract projection for validated OIF manifests.

This module performs no provider call, NiceGUI import, persistence, networking,
dynamic import, governance decision, or operation execution.
"""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .specification import InterfaceSpecification


class AbstractRenderViolation(ValueError):
    pass


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(value[k]) for k in sorted(value, key=str)})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class AbstractComponent:
    component_id: str
    component_type: str
    provider_id: str | None
    properties: Mapping[str, Any]


@dataclass(frozen=True)
class AbstractRegion:
    region_id: str
    order: int
    properties: Mapping[str, Any]
    components: Tuple[AbstractComponent, ...]


@dataclass(frozen=True)
class AbstractZone:
    zone_id: str
    label: str
    order: int
    access_mode: str
    regions: Tuple[AbstractRegion, ...]


@dataclass(frozen=True)
class AbstractRenderTree:
    interface_id: str
    title: str
    renderer_id: str
    default_zone_id: str
    zones: Tuple[AbstractZone, ...]
    source_sha256: str


def render_abstract(specification: InterfaceSpecification) -> AbstractRenderTree:
    if not isinstance(specification, InterfaceSpecification):
        raise AbstractRenderViolation("expected InterfaceSpecification")
    components = {item.component_id: item for item in specification.components}
    layouts = {item.layout_id: item for item in specification.layout}
    zones = []
    for zone in sorted(specification.navigation.zones, key=lambda item: (item.order, item.zone_id)):
        layout = layouts.get(zone.layout_id)
        if layout is None:
            raise AbstractRenderViolation("unknown layout: %s" % zone.layout_id)
        regions = []
        for region in sorted(layout.regions, key=lambda item: (item.order, item.region_id)):
            projected = []
            for component_id in region.component_ids:
                component = components.get(component_id)
                if component is None:
                    raise AbstractRenderViolation("unknown component: %s" % component_id)
                projected.append(AbstractComponent(
                    component_id=component.component_id,
                    component_type=component.component_type,
                    provider_id=component.provider_id,
                    properties=_freeze(component.properties),
                ))
            regions.append(AbstractRegion(region.region_id, region.order, _freeze(region.properties), tuple(projected)))
        zones.append(AbstractZone(zone.zone_id, zone.label, zone.order, zone.access_mode, tuple(regions)))
    return AbstractRenderTree(
        interface_id=specification.interface.interface_id,
        title=specification.interface.title,
        renderer_id=specification.interface.renderer_id,
        default_zone_id=specification.navigation.default_zone_id,
        zones=tuple(zones),
        source_sha256=specification.sha256(),
    )
