from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from nicegui import ui

from oif.review.governed_redundancy_review import CONFIRMATION_PHRASE
from oif.ui.campaign_service import OIFReviewCampaignService

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766


def _list_items(values: list[Any]) -> None:
    if not values:
        ui.label("Aucun élément").classes("text-grey-7")
        return
    with ui.column().classes("gap-1"):
        for value in values:
            ui.label(str(value)).classes("text-sm")


def build_page(service: OIFReviewCampaignService) -> None:
    workbook = service.load()
    state: dict[str, Any] = {
        "workbook": workbook,
        "filtered": list(workbook["entries"]),
        "index": 0,
    }

    ui.page_title("OIF — Revue gouvernée des redondances")
    ui.add_css(
        "body { background: #f5f7fa; } "
        ".oce-card { border: 1px solid #d8dee8; border-radius: 12px; } "
        ".mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }"
    )

    with ui.header().classes("items-center justify-between"):
        ui.label("Open Interface Fabric — OIF-0.B4.2").classes("text-h6")
        ui.badge("NiceGUI · local · gouverné", color="positive")

    with ui.column().classes("w-full max-w-screen-2xl mx-auto p-4 gap-4"):
        with ui.card().classes("w-full oce-card"):
            with ui.row().classes("w-full items-center gap-6"):
                campaign_label = ui.label()
                progress_label = ui.label()
                registry_label = ui.label("Registre inchangé pendant l’édition")
                registry_label.classes("text-positive")
            progress = ui.linear_progress(value=0).classes("w-full")

        with ui.card().classes("w-full oce-card"):
            with ui.row().classes("w-full items-end gap-3"):
                search = ui.input("Rechercher", placeholder="module, identifiant, règle...").classes("grow")
                class_filter = ui.select(
                    ["ALL"] + sorted({str(e.get("proposed_classification")) for e in workbook["entries"]}),
                    value="ALL",
                    label="Classification proposée",
                ).classes("w-64")
                state_filter = ui.select(
                    ["ALL", "PENDING", "DECIDED"],
                    value="ALL",
                    label="État de revue",
                ).classes("w-48")
                ui.button("Actualiser", icon="refresh", on_click=lambda: reload_from_disk())

        with ui.row().classes("w-full gap-4 items-stretch"):
            with ui.card().classes("w-72 oce-card"):
                ui.label("Navigation").classes("text-h6")
                position_label = ui.label()
                with ui.row().classes("w-full justify-between"):
                    previous_button = ui.button("Précédent", icon="chevron_left")
                    next_button = ui.button("Suivant", icon="chevron_right")
                candidate_list = ui.column().classes("w-full max-h-[65vh] overflow-auto gap-1")

            with ui.column().classes("grow gap-4"):
                with ui.card().classes("w-full oce-card"):
                    proposed_badge = ui.badge()
                    candidate_title = ui.label().classes("text-h5 mono")
                    candidate_meta = ui.label().classes("text-grey-7")

                with ui.row().classes("w-full gap-4 items-stretch"):
                    left_card = ui.card().classes("w-1/2 oce-card")
                    right_card = ui.card().classes("w-1/2 oce-card")

                with ui.card().classes("w-full oce-card"):
                    ui.label("Preuves et recommandation").classes("text-h6")
                    recommendation_label = ui.label()
                    decision_rule_label = ui.label().classes("mono text-sm")
                    evidence_box = ui.column().classes("w-full")
                    contradiction_box = ui.column().classes("w-full")

                with ui.card().classes("w-full oce-card"):
                    ui.label("Décision humaine gouvernée").classes("text-h6")
                    with ui.row().classes("w-full gap-3"):
                        decision_select = ui.select(
                            [""] + service.decision_options(),
                            label="Décision",
                        ).classes("w-72")
                        reviewer_id = ui.input("Identifiant du réviseur").classes("grow")
                        reviewer_role = ui.select(
                            service.role_options(),
                            value="principal_investigator",
                            label="Rôle",
                        ).classes("w-64")
                    rationale = ui.textarea("Justification fonctionnelle").props("autogrow").classes("w-full")
                    with ui.row().classes("w-full items-center justify-between"):
                        validation_hint = ui.label("20 caractères minimum; 60 pour PROBABLE_REDUNDANCY")
                        save_button = ui.button("Sauvegarder cette décision", icon="save", color="primary")

        with ui.card().classes("w-full oce-card"):
            ui.label("Application gouvernée finale").classes("text-h6")
            ui.label(
                "Cette opération est distincte de la sauvegarde. Elle valide les 104 décisions, "
                "vérifie les sources et écrit dans le registre append-only. Aucun code n’est modifié."
            )
            with ui.row().classes("w-full items-end gap-3"):
                confirmation = ui.input(
                    f"Saisir exactement : {CONFIRMATION_PHRASE}",
                    password=True,
                    password_toggle_button=True,
                ).classes("grow")
                apply_button = ui.button("Appliquer au registre", icon="gavel", color="negative")

    def current_entry() -> dict[str, Any] | None:
        if not state["filtered"]:
            return None
        state["index"] = max(0, min(state["index"], len(state["filtered"]) - 1))
        return state["filtered"][state["index"]]

    def render_dossier(card: Any, title: str, dossier: dict[str, Any]) -> None:
        card.clear()
        with card:
            ui.label(title).classes("text-h6")
            ui.label(str(dossier.get("module") or "")).classes("mono")
            ui.label(str(dossier.get("path") or "")).classes("text-sm text-grey-7")
            ui.separator()
            ui.label(f"Classification : {dossier.get('classification')}")
            ui.label(f"Entrypoints : {', '.join(dossier.get('entrypoints') or [])}")
            ui.label(f"Classes : {', '.join(dossier.get('classes') or [])}")
            ui.label(f"Fonctions : {', '.join(dossier.get('functions') or [])}")
            ui.label(f"Imports : {', '.join(dossier.get('imports') or [])}")
            consistent = bool(dossier.get("source_hash_consistent"))
            ui.badge(
                "Hash source cohérent" if consistent else "Dérive source détectée",
                color="positive" if consistent else "negative",
            )

    def update_summary() -> None:
        summary = service.summary(state["workbook"])
        campaign_label.text = f"Campagne : {summary['campaign_id']}"
        progress_label.text = (
            f"Décisions : {summary['decided_count']}/{summary['candidate_count']} "
            f"— restantes : {summary['remaining_count']}"
        )
        progress.value = summary["completion_ratio"]

    def render_list() -> None:
        candidate_list.clear()
        with candidate_list:
            for offset, entry in enumerate(state["filtered"]):
                decided = bool(entry["human_decision"].get("decision"))
                label = f"{entry['position']:03d} · {entry['left'].split('.')[-1]} ↔ {entry['right'].split('.')[-1]}"
                ui.button(
                    label,
                    icon="check_circle" if decided else "radio_button_unchecked",
                    on_click=lambda i=offset: select_index(i),
                ).props("flat dense").classes("w-full justify-start text-left")

    def render_current() -> None:
        entry = current_entry()
        total = len(state["filtered"])
        position_label.text = f"{state['index'] + 1 if total else 0} / {total}"
        previous_button.disable() if not total or state["index"] <= 0 else previous_button.enable()
        next_button.disable() if not total or state["index"] >= total - 1 else next_button.enable()
        save_button.disable() if entry is None else save_button.enable()
        if entry is None:
            candidate_title.text = "Aucun dossier correspondant aux filtres"
            candidate_meta.text = ""
            proposed_badge.text = "VIDE"
            return
        proposed_badge.text = str(entry.get("proposed_classification"))
        candidate_title.text = f"{entry['left']}  ↔  {entry['right']}"
        candidate_meta.text = (
            f"Candidat {entry['candidate_id']} · confiance {entry.get('confidence')} · "
            f"score {entry.get('combined_score')}"
        )
        recommendation_label.text = f"Recommandation : {entry.get('recommendation')}"
        decision_rule_label.text = f"Règle : {entry.get('decision_rule')}"
        render_dossier(left_card, "Interface gauche", entry.get("left_dossier") or {})
        render_dossier(right_card, "Interface droite", entry.get("right_dossier") or {})
        evidence_box.clear()
        with evidence_box:
            ui.label("Éléments favorables").classes("text-subtitle2")
            _list_items(list(entry.get("evidence") or []))
        contradiction_box.clear()
        with contradiction_box:
            ui.label("Éléments contradictoires").classes("text-subtitle2")
            _list_items(list(entry.get("contradicting_evidence") or []))
        human = entry["human_decision"]
        decision_select.value = str(human.get("decision") or "")
        reviewer_id.value = str(human.get("reviewer_id") or "")
        reviewer_role.value = str(human.get("reviewer_role") or "principal_investigator")
        rationale.value = str(human.get("rationale") or "")

    def select_index(index: int) -> None:
        state["index"] = index
        render_current()

    def apply_filters() -> None:
        state["filtered"] = service.filtered_entries(
            state["workbook"],
            query=str(search.value or ""),
            proposed_classification=str(class_filter.value or "ALL"),
            decision_state=str(state_filter.value or "ALL"),
        )
        state["index"] = 0
        render_list()
        render_current()

    def reload_from_disk() -> None:
        state["workbook"] = service.load()
        apply_filters()
        update_summary()
        ui.notify("Campagne rechargée depuis le disque", type="positive")

    def save_current() -> None:
        entry = current_entry()
        if entry is None:
            return
        try:
            service.save_decision(
                candidate_id=str(entry["candidate_id"]),
                decision=str(decision_select.value or ""),
                reviewer_id=str(reviewer_id.value or ""),
                reviewer_role=str(reviewer_role.value or ""),
                rationale=str(rationale.value or ""),
            )
        except (ValueError, PermissionError, KeyError, TypeError) as exc:
            ui.notify(str(exc), type="negative", multi_line=True)
            return
        reload_from_disk()
        ui.notify("Décision sauvegardée; registre et code inchangés", type="positive")

    def apply_final() -> None:
        try:
            result = service.apply_governed(str(confirmation.value or ""))
        except (ValueError, PermissionError, RuntimeError, KeyError, TypeError) as exc:
            ui.notify(str(exc), type="negative", multi_line=True)
            return
        confirmation.value = ""
        ui.notify(
            f"Application gouvernée terminée : {result.get('appended_count', 0)} ajout(s), "
            f"{result.get('replayed_count', 0)} rejeu(x).",
            type="positive",
            multi_line=True,
        )

    previous_button.on_click(lambda: select_index(state["index"] - 1))
    next_button.on_click(lambda: select_index(state["index"] + 1))
    save_button.on_click(save_current)
    apply_button.on_click(apply_final)
    search.on("update:model-value", lambda _: apply_filters())
    class_filter.on("update:model-value", lambda _: apply_filters())
    state_filter.on("update:model-value", lambda _: apply_filters())

    update_summary()
    render_list()
    render_current()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OIF NiceGUI governed redundancy review")
    parser.add_argument("--root", type=Path, default=Path.home() / "open-cognitive-ecology")
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    if args.host != DEFAULT_HOST and os.environ.get("OIF_ALLOW_REMOTE_UI") != "1":
        parser.error("remote binding requires OIF_ALLOW_REMOTE_UI=1")
    if not 1024 <= args.port <= 65535:
        parser.error("--port must be between 1024 and 65535")
    service = OIFReviewCampaignService(args.root, args.workbook)

    @ui.page("/")
    def index() -> None:
        build_page(service)

    print("OIF_NICEGUI_GOVERNED_REVIEW_READY")
    print(f"url=http://{args.host}:{args.port}/")
    print(f"workbook={service.workbook_path}")
    print("bind_local_only=" + str(args.host == DEFAULT_HOST).lower())
    print("automatic_code_change=false")
    print("registry_write_on_edit=false")
    ui.run(
        host=args.host,
        port=args.port,
        show=not args.no_browser,
        reload=False,
        title="OIF — Revue gouvernée",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
