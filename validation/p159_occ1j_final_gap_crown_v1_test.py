from __future__ import annotations

import io
import json
import random
import tarfile
import time
import uuid
import zipfile
from pathlib import Path

from ontology import occ_reproducibility_persistence as rp
from validation.p159_occ1j_real_reproducibility_persistence_v1_test import rebuild_real_cnp


def _snapshot(path, journal, profile_hash, state="COMPILED"):
    check = journal.verify()
    rp.atomic_write_json(path, {
        "profile_semantic_hash": profile_hash,
        "profile_state": state,
        "last_event_hash": check["last_event_hash"],
        "authorization_created": False,
        "authority_created": False,
        "execution_performed": False,
        "authorized": False,
        "pending_authorization": False,
        "p159_final_lock": False,
        "p160_opened": False,
    })


def test_rpi3_real_compilation_ignores_wall_clock_random_uuid(monkeypatch):
    reference = rebuild_real_cnp()
    monkeypatch.setattr(time, "time", lambda: 4102444800.0)
    monkeypatch.setattr(random, "random", lambda: 0.999999)
    monkeypatch.setattr(uuid, "uuid4", lambda: uuid.UUID("ffffffff-ffff-4fff-8fff-ffffffffffff"))
    rebuilt = rebuild_real_cnp()
    assert rebuilt == reference


def test_rpi11_prepare_verify_commit_is_real_and_auditable(tmp_path):
    journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    profile_hash = "abc"
    assert journal.append("PROFILE_BUILT", profile_hash, state="COMPILED",
                          timestamp_utc="2026-09-30T00:00:00Z")["status"] == "PASS"
    snap = tmp_path / "snapshot.json"
    _snapshot(snap, journal, profile_hash)
    result = rp.lifecycle_transaction(
        journal, snap, expected_state="COMPILED", event_type="VERIFIED",
        new_state="VERIFIED", profile_semantic_hash=profile_hash,
        timestamp_utc="2026-09-30T00:01:00Z",
    )
    assert result["status"] == "PASS"
    assert result["phases"] == ["PREPARE", "VERIFY", "COMMIT"]
    restored = json.loads(snap.read_text())
    assert restored["profile_state"] == "VERIFIED"
    assert rp.reconcile_state(restored, journal)["status"] == "PASS"
    assert not Path(str(snap) + ".txn").exists()


def test_rpi11_interruption_after_prepare_aborts_without_state_promotion(tmp_path):
    journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    profile_hash = "abc"
    journal.append("PROFILE_BUILT", profile_hash, state="COMPILED",
                   timestamp_utc="2026-09-30T00:00:00Z")
    snap = tmp_path / "snapshot.json"
    _snapshot(snap, journal, profile_hash)
    result = rp.lifecycle_transaction(
        journal, snap, expected_state="COMPILED", event_type="VERIFIED",
        new_state="VERIFIED", profile_semantic_hash=profile_hash,
        timestamp_utc="2026-09-30T00:01:00Z", interrupt_after="PREPARE",
    )
    assert result["status"] == "INCONCLUSIVE"
    assert json.loads(snap.read_text())["profile_state"] == "COMPILED"
    recovery = rp.recover_lifecycle_transaction(journal, snap)
    assert recovery["reason"] == "LIFECYCLE_TRANSACTION_ABORTED_PRECOMMIT"
    assert json.loads(snap.read_text())["profile_state"] == "COMPILED"


def test_rpi11_interruption_after_journal_append_recovers_uniquely(tmp_path):
    journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    profile_hash = "abc"
    journal.append("PROFILE_BUILT", profile_hash, state="COMPILED",
                   timestamp_utc="2026-09-30T00:00:00Z")
    snap = tmp_path / "snapshot.json"
    _snapshot(snap, journal, profile_hash)
    result = rp.lifecycle_transaction(
        journal, snap, expected_state="COMPILED", event_type="VERIFIED",
        new_state="VERIFIED", profile_semantic_hash=profile_hash,
        timestamp_utc="2026-09-30T00:01:00Z", interrupt_after="JOURNAL_APPENDED",
    )
    assert result["status"] == "INCONCLUSIVE"
    assert json.loads(snap.read_text())["profile_state"] == "COMPILED"
    recovery = rp.recover_lifecycle_transaction(journal, snap)
    assert recovery["reason"] == "LIFECYCLE_TRANSACTION_RECOVERED"
    restored = json.loads(snap.read_text())
    assert restored["profile_state"] == "VERIFIED"
    assert rp.reconcile_state(restored, journal)["status"] == "PASS"


def test_rpi14_restore_requires_artifact_journal_snapshot_and_authority_revalidation(tmp_path):
    profile = rebuild_real_cnp()
    env = rp.make_envelope(profile, {"kind": "backup"})
    h = env["semantic_hash"]
    journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    journal.append("PROFILE_BUILT", h, state="COMPILED", timestamp_utc="2026-09-30T00:00:00Z")
    journal.append("VERIFIED", h, state="VERIFIED", timestamp_utc="2026-09-30T00:01:00Z")
    snap = tmp_path / "snapshot.json"
    _snapshot(snap, journal, h, "VERIFIED")
    state = json.loads(snap.read_text())
    result = rp.qualify_restore(env, state, journal, expected_profile_semantic_hash=h)
    assert result["status"] == "PASS"
    assert result["reason"] == "RESTORE_ELIGIBLE_AFTER_REVALIDATION"


def test_rpi14_restore_fails_on_tampered_artifact_or_conflicting_snapshot(tmp_path):
    profile = rebuild_real_cnp()
    env = rp.make_envelope(profile, {})
    h = env["semantic_hash"]
    journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    journal.append("PROFILE_BUILT", h, state="COMPILED", timestamp_utc="2026-09-30T00:00:00Z")
    snap = tmp_path / "snapshot.json"
    _snapshot(snap, journal, h)
    state = json.loads(snap.read_text())

    tampered = dict(env)
    tampered["semantic_hash"] = "0" * 64
    assert rp.qualify_restore(tampered, state, journal, expected_profile_semantic_hash=h)["status"] == "FAIL"

    conflicting = dict(state)
    conflicting["profile_semantic_hash"] = "different"
    assert rp.qualify_restore(env, conflicting, journal, expected_profile_semantic_hash=h)["status"] == "FAIL"


def test_archive_zip_symlink_is_rejected_before_extraction(tmp_path):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (0o120777 << 16)
        zf.writestr(info, "../outside")
    dest = tmp_path / "out"
    result = rp.safe_extract_archive(archive, dest)
    assert result["status"] == "FAIL"
    assert result["reason"] == "ARCHIVE_SYMLINK_REJECTED"
    assert not dest.exists()


def test_archive_tar_symlink_escape_is_rejected_before_extraction(tmp_path):
    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w") as tf:
        info = tarfile.TarInfo("safe/link")
        info.type = tarfile.SYMTYPE
        info.linkname = "../../outside"
        tf.addfile(info)
    dest = tmp_path / "out"
    result = rp.safe_extract_archive(archive, dest)
    assert result["status"] == "FAIL"
    assert result["reason"] == "ARCHIVE_SYMLINK_REJECTED"
    assert not dest.exists()


def test_archive_safe_regular_files_extract(tmp_path):
    archive = tmp_path / "ok.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("a/profile.json", '{"ok":true}')
        zf.writestr("b/report.json", '{"status":"PASS"}')
    dest = tmp_path / "out"
    result = rp.safe_extract_archive(archive, dest)
    assert result["status"] == "PASS"
    assert (dest / "a" / "profile.json").is_file()
    assert (dest / "b" / "report.json").is_file()
