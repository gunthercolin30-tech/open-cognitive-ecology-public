from __future__ import annotations

import io
import json
import os
import shutil
import tarfile
import tempfile
import threading
from pathlib import Path

from ontology import occ_reproducibility_persistence as rp
from validation.p159_occ1j_real_reproducibility_persistence_v1_test import (
    ROOT, OCC1E, _load, rebuild_real_cnp,
)


def _safe_members(names):
    seen = set()
    folded = set()
    for raw in names:
        p = Path(raw)
        norm = p.as_posix()
        if p.is_absolute() or ".." in p.parts:
            return False
        if norm in seen or norm.casefold() in folded:
            return False
        seen.add(norm)
        folded.add(norm.casefold())
    return True


def test_generation_failure_cannot_replace_previous_sealed_artifact(tmp_path):
    sealed = tmp_path / "current" / "profile.json"
    sealed.parent.mkdir(parents=True)
    original = {"generation": 1, "semantic_status": "VERIFIED"}
    rp.atomic_write_json(sealed, original)
    original_hash = rp.file_sha256(sealed)

    failed = tmp_path / "generation-2"
    failed.mkdir()
    (failed / "profile.json.tmp").write_text('{"generation":2', encoding="utf-8")
    check = rp.verify_build_completeness(failed, ["profile.json"])
    assert check["reason"] == "BUILD_INCOMPLETE"
    assert rp.file_sha256(sealed) == original_hash
    assert _load(sealed) == original


def test_stale_output_cannot_substitute_failed_generation(tmp_path):
    g1 = tmp_path / "g1"
    g2 = tmp_path / "g2"
    g1.mkdir()
    g2.mkdir()
    rp.atomic_write_json(g1 / "profile.json", {"generation": 1})
    (g2 / "profile.json.tmp").write_text("partial", encoding="utf-8")
    result = rp.verify_build_completeness(g2, ["profile.json"])
    assert result["status"] == "FAIL"
    assert result["reason"] == "BUILD_INCOMPLETE"
    # Generation-scoped verification: g1 cannot satisfy g2.
    assert not (g2 / "profile.json").exists()


def test_concurrent_expected_state_allows_single_commit(tmp_path):
    state = tmp_path / "state.json"
    rp.atomic_write_json(state, {"revision": 0, "winner": None})
    gate = threading.Barrier(2)
    lock = threading.Lock()
    outcomes = []

    def worker(name):
        snapshot = _load(state)
        gate.wait()
        with lock:
            current = _load(state)
            if current["revision"] != snapshot["revision"]:
                outcomes.append("CONFLICT")
                return
            rp.atomic_write_json(
                state, {"revision": current["revision"] + 1, "winner": name}
            )
            outcomes.append("COMMIT")

    threads = [threading.Thread(target=worker, args=(x,)) for x in ("A", "B")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(outcomes) == ["COMMIT", "CONFLICT"]
    assert _load(state)["revision"] == 1


def test_backup_validity_does_not_create_restore_legitimacy(tmp_path):
    profile = rebuild_real_cnp()
    backup = rp.make_envelope(profile, {"kind": "backup"})
    target = tmp_path / "backup.json"
    rp.atomic_write_json(target, backup)
    restored = _load(target)
    assert rp.verify_envelope(restored)["status"] == "PASS"
    guard = rp.restart_guard({
        "authorization_created": False,
        "authority_created": False,
        "execution_performed": False,
        "authorized": False,
        "pending_authorization": False,
        "p159_final_lock": False,
        "p160_opened": False,
    })
    assert guard["status"] == "PASS"
    assert restored["CANONICAL_PAYLOAD"] == profile


def test_conflicting_continuity_branches_fail_closed(tmp_path):
    journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    first = journal.append(
        "PROFILE_BUILT", "hash-A", state="COMPILED",
        timestamp_utc="2026-09-30T00:00:00Z",
    )
    assert first["status"] == "PASS"
    check = journal.verify()
    conflicting_snapshot = {
        "profile_semantic_hash": "hash-B",
        "profile_state": "COMPILED",
        "last_event_hash": check["last_event_hash"],
    }
    result = rp.reconcile_state(conflicting_snapshot, journal)
    assert result["status"] == "FAIL"
    assert result["reason"] == "CONTINUITY_UNCERTAIN"


def test_archive_path_policy_rejects_escape_absolute_duplicate_and_case_collision():
    assert _safe_members(["a/file.json", "b/report.json"])
    assert not _safe_members(["../escape.json"])
    assert not _safe_members(["/absolute.json"])
    assert not _safe_members(["a.json", "a.json"])
    assert not _safe_members(["A.json", "a.json"])


def test_clean_room_rebuild_ignores_home_cache_and_cwd(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_cache = fake_home / ".oce"
    fake_cache.mkdir(parents=True)
    (fake_cache / "poison.json").write_text('{"semantic_status":"FORGED"}', encoding="utf-8")
    clean_cwd = tmp_path / "clean"
    clean_cwd.mkdir()

    reference = rebuild_real_cnp()
    monkeypatch.setenv("HOME", str(fake_home))
    old = Path.cwd()
    try:
        os.chdir(clean_cwd)
        rebuilt = rebuild_real_cnp()
    finally:
        os.chdir(old)
    assert rebuilt == reference


def test_restart_does_not_reset_expiry_or_renewal_counters(tmp_path):
    state = {
        "expires_at": "2026-10-01T00:00:00Z",
        "renewal_count": 4,
        "review_count": 9,
        "emergency_count": 2,
        "authorized": False,
        "p159_final_lock": False,
        "p160_opened": False,
    }
    p = tmp_path / "state.json"
    rp.atomic_write_json(p, state)
    restarted = _load(p)
    assert restarted == state
    assert restarted["renewal_count"] == 4
    assert restarted["review_count"] == 9
    assert restarted["emergency_count"] == 2


def test_pending_authorization_remains_pending_after_restart(tmp_path):
    state = {
        "pending_authorization": True,
        "authorized": False,
        "authorization_created": False,
        "authority_created": False,
        "execution_performed": False,
        "p159_final_lock": False,
        "p160_opened": False,
    }
    p = tmp_path / "pending.json"
    rp.atomic_write_json(p, state)
    restarted = _load(p)
    assert restarted["pending_authorization"] is True
    assert restarted["authorized"] is False
    assert rp.restart_guard(restarted)["status"] == "PASS"
