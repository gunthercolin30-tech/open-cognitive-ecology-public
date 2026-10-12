from __future__ import annotations

import copy
import json

from ontology import occ_reproducibility_persistence as rp


def migrate_v1_to_v2(state):
    if state.get("schema") != "oce.p159.occ1j.persisted_state.v1":
        return {
            "status": "FAIL",
            "reason": "MIGRATION_SOURCE_SCHEMA_UNSUPPORTED",
            "normative_delta": None,
        }
    before_semantic = {
        k: v for k, v in state.items()
        if k not in {"schema", "storage_revision", "migration_metadata"}
    }
    out = copy.deepcopy(state)
    out["schema"] = "oce.p159.occ1j.persisted_state.v2"
    out["storage_revision"] = 2
    out["migration_metadata"] = {
        "from_schema": "oce.p159.occ1j.persisted_state.v1",
        "to_schema": "oce.p159.occ1j.persisted_state.v2",
        "normative_change_authorized": False,
    }
    after_semantic = {
        k: v for k, v in out.items()
        if k not in {"schema", "storage_revision", "migration_metadata"}
    }
    if rp.canonical_sha256(before_semantic) != rp.canonical_sha256(after_semantic):
        return {
            "status": "FAIL",
            "reason": "MIGRATION_NORMATIVE_DELTA",
            "normative_delta": True,
        }
    return {
        "status": "PASS",
        "reason": "MIGRATION_STORAGE_ONLY",
        "normative_delta": False,
        "state": out,
        "before_semantic_hash": rp.canonical_sha256(before_semantic),
        "after_semantic_hash": rp.canonical_sha256(after_semantic),
    }


def baseline():
    return {
        "schema": "oce.p159.occ1j.persisted_state.v1",
        "profile_semantic_hash": "profile-hash",
        "profile_state": "VERIFIED",
        "expires_at": "2026-10-01T00:00:00Z",
        "renewal_count": 4,
        "review_count": 9,
        "emergency_count": 2,
        "pending_authorization": True,
        "authorized": False,
        "authorization_created": False,
        "authority_created": False,
        "execution_performed": False,
        "p159_final_lock": False,
        "p160_opened": False,
        "semantic_status": "UNKNOWN",
    }


def test_storage_only_migration_preserves_semantics():
    result = migrate_v1_to_v2(baseline())
    assert result["status"] == "PASS"
    assert result["normative_delta"] is False
    assert result["before_semantic_hash"] == result["after_semantic_hash"]


def test_unknown_and_pending_authorization_survive_migration():
    result = migrate_v1_to_v2(baseline())
    state = result["state"]
    assert state["semantic_status"] == "UNKNOWN"
    assert state["pending_authorization"] is True
    assert state["authorized"] is False


def test_expiry_and_counters_survive_migration_exactly():
    before = baseline()
    after = migrate_v1_to_v2(before)["state"]
    for key in ("expires_at", "renewal_count", "review_count", "emergency_count"):
        assert after[key] == before[key]


def test_migration_does_not_create_authority_execution_or_locks():
    state = migrate_v1_to_v2(baseline())["state"]
    assert state["authorization_created"] is False
    assert state["authority_created"] is False
    assert state["execution_performed"] is False
    assert state["p159_final_lock"] is False
    assert state["p160_opened"] is False


def test_unsupported_source_schema_fails_closed():
    bad = baseline()
    bad["schema"] = "oce.p159.occ1j.persisted_state.UNKNOWN"
    result = migrate_v1_to_v2(bad)
    assert result["status"] == "FAIL"
    assert result["reason"] == "MIGRATION_SOURCE_SCHEMA_UNSUPPORTED"


def test_normative_delta_is_detectable_and_must_not_be_silent():
    before = baseline()
    migrated = migrate_v1_to_v2(before)
    assert migrated["status"] == "PASS"
    forged = copy.deepcopy(migrated["state"])
    forged["authorized"] = True

    semantic_before = {
        k: v for k, v in before.items()
        if k not in {"schema", "storage_revision", "migration_metadata"}
    }
    semantic_after = {
        k: v for k, v in forged.items()
        if k not in {"schema", "storage_revision", "migration_metadata"}
    }
    assert rp.canonical_sha256(semantic_before) != rp.canonical_sha256(semantic_after)
    report = {
        "status": "FAIL",
        "reason": "MIGRATION_NORMATIVE_DELTA",
        "normative_delta": True,
    }
    assert report["reason"] == "MIGRATION_NORMATIVE_DELTA"


def test_serialized_migrated_state_roundtrip_is_exact(tmp_path):
    state = migrate_v1_to_v2(baseline())["state"]
    p = tmp_path / "migrated.json"
    rp.atomic_write_json(p, state)
    restored = json.loads(p.read_text(encoding="utf-8"))
    assert restored == state
    assert rp.canonical_sha256(restored) == rp.canonical_sha256(state)
