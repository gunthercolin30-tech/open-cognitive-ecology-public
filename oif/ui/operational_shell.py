"""Official NiceGUI renderer for the OIF2 read-only operational shell."""
from __future__ import annotations

import argparse
from typing import Any, Mapping

from nicegui import app, ui

from oif.application.default_providers import build_default_provider_specs
from oif.application.shell_service import OIF2ReadOnlyApplicationService
from oif.ui.civilizational_state_cards import render_civilizational_state_card
from oif.ui.navigation_model import (
    NavigationZone,
    build_navigation_model,
    filter_cards,
    resolve_active_zone,
    valid_zone_ids,
)
from oif.ui.navigation_preferences import NavigationPreferences, sanitize_preferences

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
PREFERENCES_KEY = "oif2_navigation_preferences"


def _render_provider_card(card: Mapping[str, Any]) -> None:
    if card["provider"] == "civilizational-state":
        render_civilizational_state_card(card)
        return
    with ui.expansion(str(card.get("provider", "provider")), icon="dataset").classes("w-full"):
        ui.json_editor({"content": {"json": card["payload"]}})


def _zone_color(zone: NavigationZone) -> str:
    if zone.degraded_count:
        return "warning"
    if zone.empty:
        return "grey"
    return "primary"


def _cards_by_blueprint_zone(
    snapshot: Mapping[str, Any],
) -> dict[str, tuple[Mapping[str, Any], ...]]:
    """Preserve the validated OIF2-3E zone traversal contract."""
    grouped: dict[str, tuple[Mapping[str, Any], ...]] = {}
    for zone_name, zone in snapshot["zones"].items():
        zone_cards = [
            card for card in snapshot["cards"]
            if card["zone"] == zone_name
        ]
        normalized_cards = []
        for card in zone_cards:
            normalized_cards.append(card)
        grouped[str(zone_name)] = tuple(normalized_cards)
    return grouped


def build_page(service: OIF2ReadOnlyApplicationService) -> None:
    snapshot = service.snapshot()
    cards_by_zone = _cards_by_blueprint_zone(snapshot)
    navigation = build_navigation_model(snapshot)
    zone_ids = valid_zone_ids(snapshot)
    stored = app.storage.user.get(PREFERENCES_KEY, {})
    preferences = sanitize_preferences(stored, zone_ids)
    state = {
        "active_zone": resolve_active_zone(snapshot, preferences.active_zone),
        "query": preferences.query,
        "expanded_cards": preferences.expanded_cards,
        "compact": preferences.compact,
    }

    def persist() -> None:
        app.storage.user[PREFERENCES_KEY] = NavigationPreferences(
            active_zone=state["active_zone"],
            query=state["query"],
            expanded_cards=tuple(state["expanded_cards"]),
            compact=bool(state["compact"]),
        ).as_dict()

    ui.page_title("Open Cognitive Ecology — Interface opérationnelle")
    ui.add_css(
        "body { background: #f5f7fa; } "
        ".oce-card { border: 1px solid #d8dee8; border-radius: 12px; } "
        ".mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }"
    )

    with ui.header().classes("items-center justify-between"):
        ui.label("Open Cognitive Ecology — OIF2").classes("text-h6")
        ui.badge("lecture seule", color="positive")

    with ui.left_drawer(value=True).classes("bg-white"):
        ui.label("Navigation").classes("text-h6 q-pa-md")
        navigation_container = ui.column().classes("w-full gap-1")

    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-4 gap-4"):
        with ui.card().classes("w-full oce-card"):
            ui.label("Interface opérationnelle officielle").classes("text-h5")
            ui.label(
                "Renderer NiceGUI remplaçable · services applicatifs séparés · aucune écriture directe"
            ).classes("text-grey-7")
            with ui.row().classes("gap-3 flex-wrap"):
                ui.badge(f"état: {snapshot['status']}")
                ui.badge(f"fournisseurs: {snapshot['provider_count']}")
                ui.badge("functional scope only")
            search = ui.input(
                "Rechercher un fournisseur ou une zone",
                value=state["query"],
            ).props("clearable outlined dense").classes("w-full")

        content = ui.column().classes("w-full gap-4")

    def render_navigation() -> None:
        navigation_container.clear()
        with navigation_container:
            for zone in navigation:
                label = f"{zone.label} ({zone.provider_count})"
                button = ui.button(
                    label,
                    icon="warning" if zone.degraded_count else "folder",
                    on_click=lambda _event, zone_id=zone.zone_id: select_zone(zone_id),
                ).props("flat no-caps align=left").classes("w-full justify-start")
                button.props(f"color={_zone_color(zone)}")

    def render_content() -> None:
        content.clear()
        state["active_zone"] = resolve_active_zone(snapshot, state["active_zone"])
        active = next((zone for zone in navigation if zone.zone_id == state["active_zone"]), None)
        if state["query"]:
            cards = filter_cards(snapshot, state["active_zone"], state["query"])
        elif state["active_zone"] == "overview":
            cards = [
                card
                for zone_id in snapshot["zones"]
                for card in cards_by_zone.get(str(zone_id), ())
            ]
        else:
            cards = list(cards_by_zone.get(state["active_zone"], ()))
        with content:
            with ui.card().classes("w-full oce-card"):
                ui.label(active.label if active else "Vue générale").classes("text-h6")
                if active:
                    ui.label(active.purpose).classes("text-grey-7")
                    ui.badge(active.access, color="primary")
                ui.label(f"{len(cards)} carte(s) affichée(s)").classes("text-caption text-grey-7")
            if not cards:
                with ui.card().classes("w-full oce-card"):
                    ui.label("Aucune carte ne correspond à cette vue.").classes("text-grey-6")
            for card in cards:
                _render_provider_card(card)
            degraded = snapshot.get("degraded_providers", ())
            if degraded and state["active_zone"] == "overview":
                with ui.card().classes("w-full oce-card"):
                    ui.label("Dégradation contrôlée").classes("text-h6")
                    ui.json_editor({"content": {"json": degraded}})

    def select_zone(zone_id: str) -> None:
        state["active_zone"] = resolve_active_zone(snapshot, zone_id)
        persist()
        render_content()

    def update_search(event: Any) -> None:
        state["query"] = str(getattr(event, "value", "") or "")
        persist()
        render_content()

    search.on("update:model-value", update_search)
    render_navigation()
    render_content()
    persist()


def create_default_service() -> OIF2ReadOnlyApplicationService:
    return OIF2ReadOnlyApplicationService(providers=build_default_provider_specs())



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    service = create_default_service()

    @ui.page("/")
    def index() -> None:
        build_page(service)

    ui.run(
        host=args.host,
        port=args.port,
        show=not args.no_browser,
        reload=False,
        title="Open Cognitive Ecology — OIF2",
        storage_secret="oce-oif2-local-renderer-only",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
