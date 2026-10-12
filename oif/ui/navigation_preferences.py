"""Versioned renderer-only OIF2 navigation preferences.

Preferences may be stored by the NiceGUI client/session layer. They never contain
provider payloads and never influence business, scientific, identity, memory, or
governance state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

SCHEMA_VERSION = 1
MAX_QUERY_LENGTH = 160
MAX_EXPANDED_CARDS = 64


@dataclass(frozen=True)
class NavigationPreferences:
    active_zone: str = "overview"
    query: str = ""
    expanded_cards: tuple[str, ...] = field(default_factory=tuple)
    compact: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "active_zone": self.active_zone,
            "query": self.query,
            "expanded_cards": list(self.expanded_cards),
            "compact": self.compact,
        }


def _clean_text(value: Any, maximum: int) -> str:
    return " ".join(str(value or "").strip().split())[:maximum]


def sanitize_preferences(
    value: Any,
    valid_zones: tuple[str, ...],
) -> NavigationPreferences:
    fallback_zone = "overview" if "overview" in valid_zones else (valid_zones[0] if valid_zones else "overview")
    if not isinstance(value, Mapping):
        return NavigationPreferences(active_zone=fallback_zone)
    try:
        version = int(value.get("schema_version", SCHEMA_VERSION))
    except (TypeError, ValueError):
        version = -1
    if version != SCHEMA_VERSION:
        return NavigationPreferences(active_zone=fallback_zone)
    active_zone = _clean_text(value.get("active_zone"), 64)
    if active_zone not in valid_zones:
        active_zone = fallback_zone
    query = _clean_text(value.get("query"), MAX_QUERY_LENGTH)
    expanded = value.get("expanded_cards", ())
    if not isinstance(expanded, (list, tuple)):
        expanded = ()
    cleaned = []
    for item in expanded:
        card_id = _clean_text(item, 128)
        if card_id and card_id not in cleaned:
            cleaned.append(card_id)
        if len(cleaned) >= MAX_EXPANDED_CARDS:
            break
    return NavigationPreferences(
        active_zone=active_zone,
        query=query,
        expanded_cards=tuple(cleaned),
        compact=value.get("compact") is True,
    )
