#!/usr/bin/env python3
"""Short adversarial interface crown for OIF2-3E.

This crown validates the presentation boundary of the official NiceGUI shell.
It does not modify repository files and does not read civilizational JSON
directly. It consumes the application snapshot and the renderer-only view model.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"

COMPONENT = ROOT / "oif/ui/civilizational_state_cards.py"
SHELL = ROOT / "oif/ui/operational_shell.py"
FINAL_LOCK = ROOT / "oif2_3e_nicegui_civilizational_cards_final_lock_report.json"

REAL_SOURCES = (
    ROOT / "representative_succession/civilizational_identity_preservation.json",
    ROOT / "representative_succession/representative_registry.json",
    ROOT / "representative_succession/continuity_metrics_engine.json",
    ROOT / "representative_succession/succession_execution.json",
)

ALLOWED_UI_CALLS = {
    "card",
    "row",
    "label",
    "badge",
    "expansion",
    "json_editor",
}
FORBIDDEN_UI_CALLS = {
    "button",
    "input",
    "textarea",
    "select",
    "checkbox",
    "switch",
    "upload",
    "file_picker",
    "date",
    "time",
    "slider",
    "number",
    "knob",
    "editor",
    "code",
    "run_javascript",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FakeElement:
    def __init__(self, owner: "FakeUI", kind: str, args: tuple[Any, ...], kwargs: dict[str, Any]):
        self.owner = owner
        self.kind = kind
        self.args = args
        self.kwargs = kwargs

    def classes(self, value: str) -> "FakeElement":
        self.owner.events.append(("classes", self.kind, value))
        return self

    def props(self, value: str) -> "FakeElement":
        self.owner.events.append(("props", self.kind, value))
        return self

    def __enter__(self) -> "FakeElement":
        self.owner.events.append(("enter", self.kind))
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        self.owner.events.append(("exit", self.kind))
        return False


class FakeUI:
    def __init__(self) -> None:
        self.events: list[tuple[Any, ...]] = []

    def _element(self, kind: str, *args: Any, **kwargs: Any) -> FakeElement:
        self.events.append(("call", kind, args, kwargs))
        return FakeElement(self, kind, args, kwargs)

    def card(self, *args: Any, **kwargs: Any) -> FakeElement:
        return self._element("card", *args, **kwargs)

    def row(self, *args: Any, **kwargs: Any) -> FakeElement:
        return self._element("row", *args, **kwargs)

    def label(self, *args: Any, **kwargs: Any) -> FakeElement:
        return self._element("label", *args, **kwargs)

    def badge(self, *args: Any, **kwargs: Any) -> FakeElement:
        return self._element("badge", *args, **kwargs)

    def expansion(self, *args: Any, **kwargs: Any) -> FakeElement:
        return self._element("expansion", *args, **kwargs)

    def json_editor(self, *args: Any, **kwargs: Any) -> FakeElement:
        return self._element("json_editor", *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        if name in FORBIDDEN_UI_CALLS:
            def forbidden(*args: Any, **kwargs: Any) -> FakeElement:
                fail(f"forbidden interactive NiceGUI control invoked: ui.{name}")
            return forbidden
        raise AttributeError(name)


def require_environment() -> None:
    required = (
        COMPONENT,
        SHELL,
        FINAL_LOCK,
        ROOT / "oif/application/shell_service.py",
        ROOT / "oif/application/default_providers.py",
        ROOT / "oif2_3e_fast_acceptance_suite.py",
    )
    for path in required:
        if not path.is_file():
            fail(f"required file missing: {path}")
    if not PYTHON.is_file():
        fail(f"NiceGUI interpreter missing: {PYTHON}")


def make_ready_card() -> dict[str, Any]:
    return {
        "provider": "civilizational-state",
        "zone": "memory",
        "access": "read_only",
        "payload": {
            "status": "ready",
            "available_source_count": 4,
            "invalid_source_count": 0,
            "read_only": True,
            "translation_only": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "sections": {
                "civilizational_identity": {
                    "availability": "available",
                    "status": "ready",
                    "payload": {
                        "civilization_identity": "Open Cognitive Ecology Society",
                        "civilizational_identity_preserved": True,
                    },
                },
                "representative_state": {
                    "availability": "available",
                    "status": "ready",
                    "payload": {
                        "current_representative": {
                            "civilization_identity": "Open Cognitive Ecology Society",
                            "representative_id": "REP-0001",
                            "representative_name": "Unnamed Representative",
                            "representative_is_central": False,
                            "representative_is_revocable": True,
                            "status": "active",
                        }
                    },
                },
                "continuity_state": {
                    "availability": "available",
                    "status": "ready",
                    "payload": {
                        "continuity_validated": True,
                        "continuity_decision": "maintain",
                    },
                },
                "succession_state": {
                    "availability": "available",
                    "status": "ready",
                    "payload": {
                        "latest_succession_event": {
                            "execution_status": "not_required",
                            "succession_executed": False,
                        }
                    },
                },
            },
        },
    }


def calls(ui: FakeUI, kind: str) -> list[tuple[Any, ...]]:
    return [event for event in ui.events if event[0] == "call" and event[1] == kind]


def text_arguments(ui: FakeUI, kind: str) -> list[str]:
    values: list[str] = []
    for event in calls(ui, kind):
        args = event[2]
        if args:
            values.append(str(args[0]))
    return values


def test_semantic_render_contract() -> None:
    from oif.ui.civilizational_state_cards import (
        render_civilizational_state_card,
    )

    card = make_ready_card()
    before = copy.deepcopy(card)
    fake = FakeUI()
    view = render_civilizational_state_card(card, ui_module=fake)

    assert card == before
    assert view["zone"] == "memory"
    assert view["access"] == "read_only"
    assert view["civilization_identity"] == "Open Cognitive Ecology Society"
    assert view["representative_id"] == "REP-0001"
    assert view["civilization_identity"] != view["representative_id"]
    assert view["representative_is_central"] == "non"
    assert view["representative_is_revocable"] == "oui"

    labels = text_arguments(fake, "label")
    badges = text_arguments(fake, "badge")
    expansions = text_arguments(fake, "expansion")

    required_labels = {
        "État civilisationnel",
        "Distinction civilisation / représentant",
        "Civilisation : Open Cognitive Ecology Society",
        "Représentant : REP-0001 — Unnamed Representative",
    }
    assert required_labels.issubset(set(labels))
    assert "lecture seule" in badges
    assert "central : non" in badges
    assert "révocable : oui" in badges

    for title in (
        "Identité civilisationnelle",
        "Représentant actuel",
        "Continuité",
        "Succession",
        "Données techniques",
        "Payload technique complet",
    ):
        assert title in expansions

    assert len(calls(fake, "json_editor")) == 5
    invoked = {event[1] for event in fake.events if event[0] == "call"}
    assert invoked.issubset(ALLOWED_UI_CALLS), invoked

    print("OIF2_3E_CROWN_SEMANTIC_RENDER_CONTRACT_OK")


def test_controlled_degradation_render() -> None:
    from oif.ui.civilizational_state_cards import (
        render_civilizational_state_card,
    )

    card = make_ready_card()
    card["payload"]["status"] = "degraded"
    card["payload"]["available_source_count"] = 2
    card["payload"]["invalid_source_count"] = 2
    card["payload"]["sections"]["representative_state"] = {
        "availability": "invalid",
        "status": "degraded",
        "error_type": "SchemaError",
        "payload": {},
    }
    card["payload"]["sections"].pop("succession_state")

    fake = FakeUI()
    view = render_civilizational_state_card(card, ui_module=fake)

    assert view["status"] == "degraded"
    assert view["representative_id"] == "non renseigné"
    assert len(view["sections"]) == 4

    labels = text_arguments(fake, "label")
    badges = text_arguments(fake, "badge")
    assert "Dégradation contrôlée : SchemaError" in labels
    assert "état: degraded" in badges
    assert "sources invalides: 2" in badges

    print("OIF2_3E_CROWN_CONTROLLED_DEGRADATION_RENDER_OK")


def test_determinism_and_copy_isolation() -> None:
    from oif.ui.civilizational_state_cards import (
        build_civilizational_state_view,
    )

    card = make_ready_card()
    original = copy.deepcopy(card)
    first = build_civilizational_state_view(card)
    second = build_civilizational_state_view(card)

    assert first == second
    assert card == original

    first["technical_payload"]["status"] = "tampered-view"
    first["sections"][0]["payload"]["civilization_identity"] = "tampered-view"

    assert card == original
    third = build_civilizational_state_view(card)
    assert third["status"] == "ready"
    assert third["civilization_identity"] == "Open Cognitive Ecology Society"

    print("OIF2_3E_CROWN_DETERMINISM_COPY_ISOLATION_OK")


def test_renderer_static_boundary() -> None:
    component_text = COMPONENT.read_text(encoding="utf-8")
    shell_text = SHELL.read_text(encoding="utf-8")
    component_tree = ast.parse(component_text, filename=str(COMPONENT))
    ast.parse(shell_text, filename=str(SHELL))

    forbidden_text = (
        "CivilizationalStateAdapter",
        "representative_succession",
        ".read_text(",
        ".write_text(",
        "json.load(",
        "subprocess",
        "os.system",
        "open(",
    )
    for token in forbidden_text:
        assert token not in component_text, token

    ui_calls: set[str] = set()
    for node in ast.walk(component_tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "ui_module"
        ):
            ui_calls.add(node.func.attr)

    assert ui_calls.issubset(ALLOWED_UI_CALLS), sorted(ui_calls)
    assert not ui_calls.intersection(FORBIDDEN_UI_CALLS)
    assert 'card["provider"] == "civilizational-state"' in shell_text
    assert "render_civilizational_state_card(card)" in shell_text
    assert 'ui.json_editor({"content": {"json": card["payload"]}})' in shell_text

    print("OIF2_3E_CROWN_RENDERER_STATIC_BOUNDARY_OK")


def test_real_snapshot_and_source_immutability() -> None:
    from oif.application.default_providers import build_default_provider_specs
    from oif.application.shell_service import OIF2ReadOnlyApplicationService
    from oif.ui.civilizational_state_cards import render_civilizational_state_card

    existing_sources = tuple(path for path in REAL_SOURCES if path.is_file())
    before = {str(path): digest(path) for path in existing_sources}

    service = OIF2ReadOnlyApplicationService(
        providers=build_default_provider_specs(root=ROOT)
    )
    snapshot = service.snapshot()
    cards = [
        card
        for card in snapshot["cards"]
        if card["provider"] == "civilizational-state"
    ]
    assert len(cards) == 1

    fake = FakeUI()
    view = render_civilizational_state_card(cards[0], ui_module=fake)

    assert view["zone"] == "memory"
    assert view["access"] == "read_only"
    assert view["civilization_identity"] != view["representative_id"]
    assert view["consciousness_proven"] is False
    assert view["phenomenology_undetermined"] is True

    after = {str(path): digest(path) for path in existing_sources}
    assert before == after

    print("OIF2_3E_CROWN_REAL_SNAPSHOT_SOURCE_IMMUTABILITY_OK")


def test_final_lock_integrity() -> None:
    report = json.loads(FINAL_LOCK.read_text(encoding="utf-8"))

    assert report["status"] == "locked"
    assert report["provider_name"] == "civilizational-state"
    assert report["zone"] == "memory"
    assert report["renderer_read_only"] is True
    assert report["direct_adapter_import_absent"] is True
    assert report["direct_persistent_state_read_absent"] is True
    assert report["business_logic_in_renderer_absent"] is True
    assert report["species_representative_distinction_visible"] is True
    assert report["controlled_degradation_validated"] is True
    assert report["generic_provider_rendering_preserved"] is True
    assert report["consciousness_proven"] is False
    assert report["phenomenology_undetermined"] is True

    for relative, expected in report["sha256"].items():
        path = ROOT / relative
        assert path.is_file(), relative
        assert digest(path) == expected, relative

    print("OIF2_3E_CROWN_FINAL_LOCK_INTEGRITY_OK")


def unused_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_nicegui_server_smoke() -> None:
    port = unused_local_port()
    command = [
        str(PYTHON),
        "-m",
        "oif.ui.operational_shell",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--no-browser",
    ]
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    output = ""
    try:
        deadline = time.monotonic() + 15.0
        response_ok = False
        while time.monotonic() < deadline:
            if process.poll() is not None:
                break
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}",
                    timeout=1.0,
                ) as response:
                    body = response.read(4096)
                    assert response.status == 200
                    assert body
                    response_ok = True
                    break
            except Exception:
                time.sleep(0.15)

        if not response_ok:
            if process.stdout is not None:
                output = process.stdout.read()
            fail(
                "NiceGUI server did not become reachable; output="
                + output[-2000:]
            )
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5.0)
        if process.stdout is not None:
            output += process.stdout.read()

    # SIGTERM is an acceptable controlled stop for this short-lived smoke test.
    assert process.returncode is not None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(1.0)
        assert probe.connect_ex(("127.0.0.1", port)) != 0

    print("OIF2_3E_CROWN_NICEGUI_SERVER_SMOKE_OK")


def main() -> int:
    started = time.monotonic()
    require_environment()

    test_semantic_render_contract()
    test_controlled_degradation_render()
    test_determinism_and_copy_isolation()
    test_renderer_static_boundary()
    test_real_snapshot_and_source_immutability()
    test_final_lock_integrity()
    test_nicegui_server_smoke()

    elapsed = time.monotonic() - started
    print(
        "OIF2_3E_INTERFACE_VALIDATION_CROWN_OK "
        f"total_seconds={elapsed:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
