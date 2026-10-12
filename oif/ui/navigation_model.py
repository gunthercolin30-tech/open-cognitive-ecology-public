"""Pure, deterministic navigation model for the OIF2 operational shell.

This module consumes only the application snapshot. It does not import NiceGUI,
adapters, persistence, runtime producers, or governance executors.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

OVERVIEW_ZONE = "overview"


@dataclass(frozen=True)
class NavigationZone:
    zone_id: str
    label: str
    purpose: str
    access: str
    order: int
    provider_count: int
    degraded_count: int
    empty: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "label": self.label,
            "purpose": self.purpose,
            "access": self.access,
            "order": self.order,
            "provider_count": self.provider_count,
            "degraded_count": self.degraded_count,
            "empty": self.empty,
        }


_ZONE_LABELS = {
    "overview": "Vue générale",
    "runtime": "Runtime",
    "experiments": "Expériences",
    "science": "Science",
    "memory": "Mémoire",
    "governance": "Gouvernance",
    "system": "Système",
}


def _mapping(value: Any) -> dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def normalize_query(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def build_navigation_model(snapshot: Mapping[str, Any]) -> tuple[NavigationZone, ...]:
    source = _mapping(snapshot)
    zones = _mapping(source.get("zones"))
    cards = tuple(_mapping(card) for card in source.get("cards", ()) if isinstance(card, Mapping))
    degraded = tuple(
        _mapping(item)
        for item in source.get("degraded_providers", ())
        if isinstance(item, Mapping)
    )
    model = []
    for order, (zone_id, descriptor_value) in enumerate(zones.items()):
        descriptor = _mapping(descriptor_value)
        provider_count = sum(1 for card in cards if card.get("zone") == zone_id)
        degraded_count = sum(1 for item in degraded if item.get("zone") == zone_id)
        model.append(
            NavigationZone(
                zone_id=str(zone_id),
                label=_ZONE_LABELS.get(str(zone_id), str(zone_id).replace("_", " ").title()),
                purpose=str(descriptor.get("purpose", "")),
                access=str(descriptor.get("access", "read_only")),
                order=order,
                provider_count=provider_count,
                degraded_count=degraded_count,
                empty=provider_count == 0,
            )
        )
    return tuple(model)


def valid_zone_ids(snapshot: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(zone.zone_id for zone in build_navigation_model(snapshot))


def resolve_active_zone(snapshot: Mapping[str, Any], requested: Any) -> str:
    zones = valid_zone_ids(snapshot)
    candidate = str(requested or "").strip()
    if candidate in zones:
        return candidate
    if OVERVIEW_ZONE in zones:
        return OVERVIEW_ZONE
    return zones[0] if zones else OVERVIEW_ZONE


def searchable_card_text(card: Mapping[str, Any], zone: NavigationZone | None = None) -> str:
    source = _mapping(card)
    values = [source.get("provider"), source.get("zone"), source.get("access")]
    if zone is not None:
        values.extend((zone.label, zone.purpose, zone.access))
    return normalize_query(" ".join(str(value or "") for value in values))


def filter_cards(
    snapshot: Mapping[str, Any],
    active_zone: Any,
    query: Any = "",
) -> tuple[dict[str, Any], ...]:
    source = _mapping(snapshot)
    zone_id = resolve_active_zone(source, active_zone)
    normalized_query = normalize_query(query)
    zones_by_id = {zone.zone_id: zone for zone in build_navigation_model(source)}
    result = []
    for card_value in source.get("cards", ()):
        if not isinstance(card_value, Mapping):
            continue
        card = _mapping(card_value)
        if zone_id != OVERVIEW_ZONE and card.get("zone") != zone_id:
            continue
        if normalized_query:
            zone = zones_by_id.get(str(card.get("zone")))
            if normalized_query not in searchable_card_text(card, zone):
                continue
        result.append(card)
    return tuple(result)


def filter_zones(
    zones: Iterable[NavigationZone],
    query: Any = "",
) -> tuple[NavigationZone, ...]:
    normalized_query = normalize_query(query)
    if not normalized_query:
        return tuple(zones)
    return tuple(
        zone
        for zone in zones
        if normalized_query in normalize_query(
            f"{zone.zone_id} {zone.label} {zone.purpose} {zone.access}"
        )
    )
