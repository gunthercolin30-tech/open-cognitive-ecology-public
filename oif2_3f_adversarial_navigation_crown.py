#!/usr/bin/env python3
"""Adversarial validation crown for OIF2-3F Operational Navigation Layer.

Read-only campaign. It never modifies repository state. Temporary artifacts are
created only under an isolated TemporaryDirectory and removed automatically.
"""
from __future__ import annotations

import ast
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sample_snapshot() -> dict[str, Any]:
    return {
        "status": "operational",
        "provider_count": 3,
        "zones": {
            "overview": {"purpose": "Vue consolidée", "access": "read_only"},
            "runtime": {"purpose": "Santé du runtime", "access": "read_only"},
            "experiments": {"purpose": "Expériences", "access": "read_only"},
            "science": {"purpose": "Validation scientifique", "access": "read_only"},
            "memory": {"purpose": "Mémoire civilisationnelle", "access": "read_only"},
            "governance": {"purpose": "Gouvernance", "access": "read_only"},
            "system": {"purpose": "Système", "access": "read_only"},
        },
        "cards": [
            {
                "provider": "runtime-health",
                "zone": "runtime",
                "access": "read_only",
                "payload": {"secret_payload_only_token": "DO_NOT_INDEX_7F91"},
            },
            {
                "provider": "validation-report",
                "zone": "science",
                "access": "read_only",
                "payload": {"status": "ok"},
            },
            {
                "provider": "civilizational-state",
                "zone": "memory",
                "access": "read_only",
                "payload": {"representative_is_revocable": True},
            },
        ],
        "degraded_providers": [],
    }


def test_model_adversaries() -> None:
    from oif.ui.navigation_model import (
        OVERVIEW_ZONE,
        build_navigation_model,
        filter_cards,
        filter_zones,
        normalize_query,
        resolve_active_zone,
        searchable_card_text,
        valid_zone_ids,
    )

    snapshot = sample_snapshot()
    before = deepcopy(snapshot)

    model = build_navigation_model(snapshot)
    require(len(model) == 7, "all blueprint zones must remain visible")
    require(valid_zone_ids(snapshot)[0] == OVERVIEW_ZONE, "overview must remain first")
    require(resolve_active_zone(snapshot, "unknown") == OVERVIEW_ZONE, "unknown zone must fail safe")
    require(resolve_active_zone({"zones": {}}, "unknown") == OVERVIEW_ZONE, "empty model fallback")

    require(len(filter_cards(snapshot, "runtime")) == 1, "runtime zone filtering failed")
    require(len(filter_cards(snapshot, "overview")) == 3, "overview aggregation failed")
    require(len(filter_cards(snapshot, "overview", "science")) == 1, "zone metadata search failed")
    require(len(filter_cards(snapshot, "overview", "DO_NOT_INDEX_7F91")) == 0, "payload was indexed")
    require("DO_NOT_INDEX_7F91" not in searchable_card_text(snapshot["cards"][0]), "payload leakage")

    query = "   MéMoire    CIVILISATIONNELLE  "
    require(normalize_query(query) == "mémoire civilisationnelle", "query normalization failed")
    require(any(z.zone_id == "memory" for z in filter_zones(model, query)), "accented zone search failed")

    duplicate_snapshot = deepcopy(snapshot)
    duplicate_snapshot["cards"].append(deepcopy(duplicate_snapshot["cards"][0]))
    duplicated = filter_cards(duplicate_snapshot, "runtime")
    require(len(duplicated) == 2, "navigation model must not silently rewrite provider cardinality")

    malformed = {
        "zones": {"overview": None, "runtime": "bad"},
        "cards": [None, 4, "x", {"provider": "p", "zone": "runtime"}],
        "degraded_providers": [None, {"zone": "runtime"}],
    }
    malformed_model = build_navigation_model(malformed)
    require(len(malformed_model) == 2, "malformed descriptors must degrade safely")
    runtime = next(zone for zone in malformed_model if zone.zone_id == "runtime")
    require(runtime.provider_count == 1 and runtime.degraded_count == 1, "degraded counts incorrect")

    require(snapshot == before, "navigation model mutated the application snapshot")
    print("OIF2_3F_CROWN_MODEL_ADVERSARIES_OK")


def test_preferences_adversaries() -> None:
    from oif.ui.navigation_preferences import (
        MAX_EXPANDED_CARDS,
        MAX_QUERY_LENGTH,
        NavigationPreferences,
        sanitize_preferences,
    )

    zones = ("overview", "runtime", "science")
    fallback = sanitize_preferences(None, zones)
    require(fallback.active_zone == "overview", "non-mapping preference fallback failed")

    corrupt = sanitize_preferences(
        {
            "schema_version": "not-an-int",
            "active_zone": "runtime",
            "query": "x",
            "expanded_cards": ["p"],
            "compact": True,
        },
        zones,
    )
    require(corrupt == NavigationPreferences(active_zone="overview"), "corrupt schema must reset")

    huge = sanitize_preferences(
        {
            "schema_version": 1,
            "active_zone": "deleted-zone",
            "query": " q " * (MAX_QUERY_LENGTH * 4),
            "expanded_cards": ["a", "a"] + [f"card-{i}" for i in range(MAX_EXPANDED_CARDS * 3)],
            "compact": 1,
            "payload": {"must": "not persist"},
        },
        zones,
    )
    require(huge.active_zone == "overview", "deleted zone fallback failed")
    require(len(huge.query) <= MAX_QUERY_LENGTH, "query cap bypassed")
    require(len(huge.expanded_cards) <= MAX_EXPANDED_CARDS, "expanded card cap bypassed")
    require(len(huge.expanded_cards) == len(set(huge.expanded_cards)), "expanded card deduplication failed")
    require(huge.compact is False, "compact must accept only literal True")
    serialized = huge.as_dict()
    require(set(serialized) == {"schema_version", "active_zone", "query", "expanded_cards", "compact"}, "preference whitelist violated")
    require("payload" not in json.dumps(serialized), "provider payload persisted in preferences")
    print("OIF2_3F_CROWN_PREFERENCES_ADVERSARIES_OK")


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_architectural_boundaries() -> None:
    navigation_model = ROOT / "oif/ui/navigation_model.py"
    preferences = ROOT / "oif/ui/navigation_preferences.py"
    shell = ROOT / "oif/ui/operational_shell.py"
    for path in (navigation_model, preferences, shell):
        require(path.is_file(), f"missing required file: {path}")
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    model_text = navigation_model.read_text(encoding="utf-8")
    prefs_text = preferences.read_text(encoding="utf-8")
    shell_text = shell.read_text(encoding="utf-8")
    # Structural checks must inspect executable imports, not arbitrary text.
    # Words such as "persistence" may legitimately occur in comments, docstrings,
    # type names, or explanatory constants without creating a dependency.
    model_roots = imported_roots(navigation_model)
    prefs_roots = imported_roots(preferences)
    forbidden_model_roots = {"nicegui", "subprocess", "sqlite3"}
    require(
        model_roots.isdisjoint(forbidden_model_roots) and "oif" not in model_roots,
        f"pure model boundary violated by imports: {sorted(model_roots & forbidden_model_roots)}",
    )
    require(
        prefs_roots.isdisjoint({"nicegui"}) and "oif" not in prefs_roots,
        f"preference boundary violated by imports: {sorted(prefs_roots)}",
    )
    require("from oif.application.shell_service import OIF2ReadOnlyApplicationService" in shell_text, "application service boundary missing")
    require("oif.adapters" not in shell_text, "renderer imports adapter directly")
    require("open(" not in shell_text and "Path(" not in shell_text, "renderer appears to access persistence/files")
    require('card["provider"] == "civilizational-state"' in shell_text, "OIF2-3E lexical contract lost")
    require('for zone_name, zone in snapshot["zones"].items()' in shell_text, "zone traversal contract lost")
    require('ui.json_editor({"content": {"json": card["payload"]}})' in shell_text, "generic renderer contract lost")

    require("nicegui" not in model_roots and "oif" not in model_roots, "model imports framework/application package")
    print("OIF2_3F_CROWN_ARCHITECTURAL_BOUNDARIES_OK")


def wait_for_port(host: str, port: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.25):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def test_real_server_lifecycle() -> None:
    python = Path(sys.executable)
    require(python.exists(), "active Python interpreter is missing")
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    with tempfile.TemporaryDirectory(prefix="oif2_3f_crown_") as temp_dir:
        proc = subprocess.Popen(
            [str(python), "-m", "oif.ui.operational_shell", "--no-browser"],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        try:
            require(wait_for_port("127.0.0.1", 8766, 12.0), "NiceGUI server did not bind to 127.0.0.1:8766")
            with socket.create_connection(("127.0.0.1", 8766), timeout=2.0) as sock:
                sock.sendall(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n")
                response = sock.recv(512)
            require(b"HTTP/1.1 200" in response or b"HTTP/1.1 302" in response, "unexpected HTTP response")
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=3)
            output = proc.stdout.read() if proc.stdout else ""
            (Path(temp_dir) / "server_output.txt").write_text(output, encoding="utf-8")
        require(proc.returncode in (0, -signal.SIGTERM, 143), f"unexpected server exit code: {proc.returncode}\n{output}")
        require("Traceback" not in output, f"server lifecycle emitted traceback:\n{output}")
    print("OIF2_3F_CROWN_REAL_SERVER_LIFECYCLE_OK")


def test_final_lock_integrity() -> None:
    import hashlib

    report = ROOT / "oif2_3f_operational_navigation_final_lock_report.json"
    require(report.is_file(), "final lock report missing")
    data = json.loads(report.read_text(encoding="utf-8"))

    require(isinstance(data, dict), "final lock report must be a JSON object")
    require(data.get("primitive") == "oif2_operational_navigation_layer", "unexpected final lock primitive")
    require(data.get("status") == "locked", "final lock status is not locked")
    require(data.get("read_only_renderer") is True, "read-only renderer invariant violated")
    require(data.get("blueprint_zones_only") is True, "blueprint-zone invariant violated")
    require(data.get("provider_payload_search_absent") is True, "payload-search boundary violated")
    require(data.get("direct_adapter_import_absent") is True, "direct-adapter boundary violated")
    require(data.get("direct_business_persistence_absent") is True, "business-persistence boundary violated")
    require(data.get("renderer_state_local_only") is True, "renderer-state boundary violated")
    require(data.get("controlled_degradation_validated") is True, "degradation validation missing")

    require(data.get("consciousness_proven") is False, "epistemic invariant violated")
    require(data.get("subjectivity_proven") is False, "subjectivity invariant violated")
    require(data.get("functional_conclusion_only") is True, "functional-only invariant violated")
    require(data.get("phenomenology_undetermined") is True, "phenomenology invariant violated")

    hashes = data.get("sha256")
    require(isinstance(hashes, dict) and hashes, "final lock hash manifest missing")
    for rel, expected in hashes.items():
        require(isinstance(rel, str) and rel and not Path(rel).is_absolute(), f"invalid manifest path: {rel!r}")
        require(isinstance(expected, str) and len(expected) == 64, f"invalid SHA-256 for {rel!r}")
        target = ROOT / rel
        require(target.is_file(), f"locked artifact missing: {rel}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        require(actual == expected, f"locked artifact hash mismatch: {rel}")

    print("OIF2_3F_CROWN_FINAL_LOCK_INTEGRITY_OK")


def main() -> int:
    require(ROOT.is_dir(), f"repository root missing: {ROOT}")
    os.chdir(ROOT)
    test_model_adversaries()
    test_preferences_adversaries()
    test_architectural_boundaries()
    test_real_server_lifecycle()
    test_final_lock_integrity()
    print("OIF2_3F_ADVERSARIAL_NAVIGATION_CROWN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
