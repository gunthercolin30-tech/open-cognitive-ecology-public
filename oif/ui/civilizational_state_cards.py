"""Pure presentation mapping and NiceGUI rendering for civilizational-state cards.

This module consumes only the already translated shell card payload. It must not
read persistent state, instantiate adapters, execute producers, or decide
civilizational status.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

PROVIDER_NAME = "civilizational-state"
SECTION_ORDER = (
    "civilizational_identity",
    "representative_state",
    "continuity_state",
    "succession_state",
)
SECTION_TITLES = {
    "civilizational_identity": "Identité civilisationnelle",
    "representative_state": "Représentant actuel",
    "continuity_state": "Continuité",
    "succession_state": "Succession",
}


def _mapping(value: Any) -> dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _text(value: Any, fallback: str = "non renseigné") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _yes_no(value: Any) -> str:
    if value is True:
        return "oui"
    if value is False:
        return "non"
    return "non renseigné"


def build_civilizational_state_view(card: Mapping[str, Any]) -> dict[str, Any]:
    """Build a renderer-only view model without deriving any business status."""
    source_card = _mapping(card)
    payload = _mapping(source_card.get("payload"))
    sections = _mapping(payload.get("sections"))

    identity_descriptor = _mapping(sections.get("civilizational_identity"))
    identity = _mapping(identity_descriptor.get("payload"))

    representative_descriptor = _mapping(sections.get("representative_state"))
    representative_root = _mapping(representative_descriptor.get("payload"))
    representative = _mapping(representative_root.get("current_representative"))

    continuity_descriptor = _mapping(sections.get("continuity_state"))
    continuity = _mapping(continuity_descriptor.get("payload"))

    succession_descriptor = _mapping(sections.get("succession_state"))
    succession_root = _mapping(succession_descriptor.get("payload"))
    succession = _mapping(succession_root.get("latest_succession_event"))
    if not succession:
        succession = _mapping(succession_root.get("succession_event"))
    if not succession:
        succession = succession_root

    section_views = []
    for name in SECTION_ORDER:
        descriptor = _mapping(sections.get(name))
        section_views.append({
            "name": name,
            "title": SECTION_TITLES[name],
            "availability": _text(descriptor.get("availability"), "absent"),
            "status": _text(descriptor.get("status"), "unknown"),
            "payload": _mapping(descriptor.get("payload")),
            "error_type": descriptor.get("error_type"),
        })

    return {
        "provider": _text(source_card.get("provider"), PROVIDER_NAME),
        "zone": _text(source_card.get("zone"), "memory"),
        "access": _text(source_card.get("access"), "read_only"),
        "status": _text(payload.get("status"), "unavailable"),
        "available_source_count": payload.get("available_source_count", 0),
        "invalid_source_count": payload.get("invalid_source_count", 0),
        "read_only": payload.get("read_only") is True,
        "translation_only": payload.get("translation_only") is True,
        "civilization_identity": _text(
            representative.get("civilization_identity")
            or identity.get("civilization_identity")
            or identity.get("civilization_name")
        ),
        "representative_id": _text(representative.get("representative_id")),
        "representative_name": _text(representative.get("representative_name")),
        "representative_status": _text(representative.get("status"), "unknown"),
        "representative_is_central": _yes_no(
            representative.get("representative_is_central")
        ),
        "representative_is_revocable": _yes_no(
            representative.get("representative_is_revocable")
        ),
        "identity_preserved": _yes_no(
            identity.get("civilizational_identity_preserved")
        ),
        "continuity_validated": _yes_no(
            continuity.get("continuity_validated")
        ),
        "continuity_decision": _text(
            continuity.get("continuity_decision"), "non renseignée"
        ),
        "succession_execution_status": _text(
            succession.get("execution_status"), "unknown"
        ),
        "succession_executed": _yes_no(
            succession.get("succession_executed")
        ),
        "sections": section_views,
        "technical_payload": deepcopy(payload),
        "functional_conclusion_only": payload.get(
            "functional_conclusion_only"
        ) is True,
        "phenomenology_undetermined": payload.get(
            "phenomenology_undetermined"
        ) is True,
        "consciousness_proven": payload.get("consciousness_proven") is True,
    }


def render_civilizational_state_card(
    card: Mapping[str, Any],
    ui_module: Any = None,
) -> dict[str, Any]:
    """Render one card; return its pure view model for deterministic testing."""
    if ui_module is None:
        from nicegui import ui as ui_module

    view = build_civilizational_state_view(card)

    with ui_module.card().classes("w-full oce-card bg-white"):
        with ui_module.row().classes("w-full items-center justify-between"):
            ui_module.label("État civilisationnel").classes("text-h6")
            ui_module.badge(f"état: {view['status']}")
        with ui_module.row().classes("gap-2 flex-wrap"):
            ui_module.badge(f"sources disponibles: {view['available_source_count']}")
            ui_module.badge(f"sources invalides: {view['invalid_source_count']}")
            ui_module.badge("lecture seule", color="positive")

        with ui_module.card().classes("w-full bg-grey-1"):
            ui_module.label("Distinction civilisation / représentant").classes(
                "text-subtitle1"
            )
            ui_module.label(
                f"Civilisation : {view['civilization_identity']}"
            )
            ui_module.label(
                f"Représentant : {view['representative_id']} — "
                f"{view['representative_name']}"
            )
            with ui_module.row().classes("gap-2 flex-wrap"):
                ui_module.badge(
                    f"central : {view['representative_is_central']}"
                )
                ui_module.badge(
                    f"révocable : {view['representative_is_revocable']}"
                )
                ui_module.badge(
                    f"statut : {view['representative_status']}"
                )

        summary_by_name = {
            "civilizational_identity": [
                ("identité préservée", view["identity_preserved"]),
            ],
            "representative_state": [
                ("identifiant", view["representative_id"]),
                ("nom", view["representative_name"]),
            ],
            "continuity_state": [
                ("continuité validée", view["continuity_validated"]),
                ("décision", view["continuity_decision"]),
            ],
            "succession_state": [
                ("exécution", view["succession_execution_status"]),
                ("succession exécutée", view["succession_executed"]),
            ],
        }
        for section in view["sections"]:
            with ui_module.expansion(
                section["title"], icon="account_tree"
            ).classes("w-full"):
                with ui_module.row().classes("gap-2 flex-wrap"):
                    ui_module.badge(
                        f"disponibilité: {section['availability']}"
                    )
                    ui_module.badge(f"statut: {section['status']}")
                if section["error_type"]:
                    ui_module.label(
                        f"Dégradation contrôlée : {section['error_type']}"
                    ).classes("text-negative")
                for label, value in summary_by_name[section["name"]]:
                    ui_module.label(f"{label.capitalize()} : {value}")
                with ui_module.expansion(
                    "Données techniques", icon="data_object"
                ).classes("w-full"):
                    ui_module.json_editor({
                        "content": {"json": section["payload"]}
                    })

        with ui_module.expansion(
            "Payload technique complet", icon="code"
        ).classes("w-full"):
            ui_module.json_editor({
                "content": {"json": view["technical_payload"]}
            })

    return view
