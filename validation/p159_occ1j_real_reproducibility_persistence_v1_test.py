from __future__ import annotations

import json
import os
from pathlib import Path

from ontology import occ_compiled_normative_profile as cnp
from ontology import occ_reproducibility_persistence as rp

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "validation_artifacts" / "p159"
OCC1C = A / "occ1c" / "compiled_normative_profile_v1.json"
OCC1E = A / "occ1e" / "compiled_normative_profile_v1.json"
SCHEMA = ROOT / "schemas" / "p159_occ1e_compiled_normative_profile_v1.schema.json"
COMPILER = ROOT / "ontology" / "occ_constitutional_compiler.py"
DEPENDENCY_REGISTRY = ROOT / "dependency_registry.py"
SOURCE_ROOT = ROOT / "normative" / "occ1a"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _static_report() -> Path:
    candidates = [
        A / "occ1d" / "static_constitutional_check_report_v1_2.json",
        A / "occ1d" / "static_constitutional_check_report_v1.json",
    ]
    p = next((x for x in candidates if x.exists()), None)
    assert p is not None, "OCC1D_STATIC_REPORT_REQUIRED"
    return p


def rebuild_real_cnp():
    base = _load(OCC1C)
    return cnp.build_profile(
        base,
        cnp.file_sha256(OCC1C),
        cnp.file_sha256(COMPILER),
        cnp.file_sha256(SCHEMA),
        cnp.file_sha256(_static_report()),
    )


def source_files():
    return sorted(
        (p for p in SOURCE_ROOT.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(SOURCE_ROOT).as_posix(),
    )


def identity(files=None):
    return rp.build_identity(
        files or source_files(),
        nir_schema_version="P159-OCC1B-NIR",
        compiler_version=getattr(cnp, "VERSION", "UNKNOWN"),
        compiler_file=COMPILER,
        dependency_manifest_file=DEPENDENCY_REGISTRY,
        canonicalizer_version="python-json-sort-keys-compact-utf8",
        checker_version="P159-OCC1D",
        build_profile="P159-OCC1J-R3",
    )


def test_real_cnp_rebuild_matches_locked_occ1e_artifact():
    reference = _load(OCC1E)
    rebuilt = rebuild_real_cnp()
    assert cnp.verify_profile(reference)["status"] == "PASS"
    assert cnp.verify_profile(rebuilt)["status"] == "PASS"
    assert rebuilt == reference


def test_real_rebuild_is_cwd_independent(tmp_path):
    before = rebuild_real_cnp()
    old = Path.cwd()
    try:
        os.chdir(tmp_path)
        after = rebuild_real_cnp()
    finally:
        os.chdir(old)
    assert after == before


def test_source_enumeration_order_does_not_change_build_identity():
    files = source_files()
    assert identity(files)["source_package_hash"] == identity(list(reversed(files)))["source_package_hash"]
    assert identity(files)["build_identity_hash"] == identity(list(reversed(files)))["build_identity_hash"]


def test_execution_metadata_does_not_change_real_cnp_semantics():
    profile = rebuild_real_cnp()
    a = rp.make_envelope(profile, {"run_id": "A", "timestamp": "2026-01-01T00:00:00Z"})
    b = rp.make_envelope(profile, {"run_id": "B", "timestamp": "2030-12-31T23:59:59Z"})
    assert a["semantic_hash"] == b["semantic_hash"]
    assert a["artifact_hash"] != b["artifact_hash"]


def test_real_profile_persistence_roundtrip_and_unknown_preservation(tmp_path):
    profile = rebuild_real_cnp()
    envelope = rp.make_envelope(profile, {"purpose": "OCC-1J persistence qualification"})
    target = tmp_path / "generation-1" / "profile_envelope.json"
    rp.atomic_write_json(target, envelope)
    restored = _load(target)
    assert rp.verify_envelope(restored)["status"] == "PASS"
    assert restored["semantic_hash"] == envelope["semantic_hash"]
    statuses_before = [
        r.get("uncertainty_semantics", {}).get("semantic_status")
        for r in profile["rules"]
    ]
    statuses_after = [
        r.get("uncertainty_semantics", {}).get("semantic_status")
        for r in restored["CANONICAL_PAYLOAD"]["rules"]
    ]
    # Real-state persistence claim: preserve exactly what the locked CNP contains.
    # Do not require the real artifact to contain a particular uncertainty label.
    assert statuses_after == statuses_before

    # Separate synthetic sentinel: prove UNKNOWN itself survives the same
    # envelope -> atomic JSON persistence -> reload path without promoting it.
    unknown_envelope = rp.make_envelope(
        {"semantic_status": "UNKNOWN", "authorized": False},
        {"purpose": "OCC-1J UNKNOWN persistence sentinel"},
    )
    unknown_target = tmp_path / "generation-unknown" / "profile_envelope.json"
    rp.atomic_write_json(unknown_target, unknown_envelope)
    unknown_restored = _load(unknown_target)
    assert rp.verify_envelope(unknown_restored)["status"] == "PASS"
    assert unknown_restored["CANONICAL_PAYLOAD"]["semantic_status"] == "UNKNOWN"
    assert unknown_restored["CANONICAL_PAYLOAD"]["authorized"] is False


def test_real_profile_restart_reconciles_without_authority_creation(tmp_path):
    profile = rebuild_real_cnp()
    envelope = rp.make_envelope(profile, {})
    journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    built = journal.append(
        "PROFILE_BUILT", envelope["semantic_hash"],
        state="COMPILED", timestamp_utc="2026-09-30T00:00:00Z",
    )
    assert built["status"] == "PASS"
    verified = journal.append(
        "VERIFIED", envelope["semantic_hash"],
        state="VERIFIED", timestamp_utc="2026-09-30T00:01:00Z",
    )
    assert verified["status"] == "PASS"
    check = journal.verify()
    snapshot = {
        "profile_semantic_hash": envelope["semantic_hash"],
        "profile_state": "VERIFIED",
        "last_event_hash": check["last_event_hash"],
        "authorization_created": False,
        "authority_created": False,
        "execution_performed": False,
        "pending_authorization": False,
        "authorized": False,
        "p159_final_lock": False,
        "p160_opened": False,
    }
    rp.atomic_write_json(tmp_path / "snapshot.json", snapshot)
    restarted_snapshot = _load(tmp_path / "snapshot.json")
    restarted_journal = rp.NormativeLifecycleJournal(tmp_path / "journal.jsonl")
    assert rp.reconcile_state(restarted_snapshot, restarted_journal)["status"] == "PASS"
    assert rp.restart_guard(restarted_snapshot)["status"] == "PASS"


def test_interrupted_generation_cannot_be_mistaken_for_complete_build(tmp_path):
    generation = tmp_path / "generation-2"
    generation.mkdir()
    (generation / "profile.json.tmp").write_text('{"partial":true}', encoding="utf-8")
    result = rp.verify_build_completeness(
        generation,
        ["profile.json", "reproducibility_report.json", "persistence_report.json"],
    )
    assert result["status"] == "FAIL"
    assert result["reason"] == "BUILD_INCOMPLETE"


def test_clock_rollback_remains_epistemically_uncertain():
    result = rp.clock_integrity(
        "2026-09-30T10:00:00Z", "2026-09-30T09:00:00Z", tolerance_seconds=1
    )
    assert result["status"] == "INCONCLUSIVE"
    assert result["reason"] == "CLOCK_INTEGRITY_UNCERTAIN"


def test_real_reports_remain_separate_and_non_authorizing():
    reference = _load(OCC1E)
    rebuilt = rebuild_real_cnp()
    ref_env = rp.make_envelope(reference, {"kind": "historical"})
    new_env = rp.make_envelope(rebuilt, {"kind": "clean-rebuild"})
    rr = rp.reproducibility_report(ref_env, new_env, identity())
    state = {
        "profile_semantic_hash": new_env["semantic_hash"],
        "profile_state": "VERIFIED",
        "authorization_created": False,
        "execution_performed": False,
        "p159_final_lock": False,
        "p160_opened": False,
    }
    pr = rp.persistence_report(state, json.loads(json.dumps(state)), {"status": "PASS"})
    assert rr["status"] == "PASS"
    assert pr["status"] == "PASS"
    assert rr["schema"] != pr["schema"]
    for report in (rr, pr):
        assert report["authorization_created"] is False
        assert report["execution_performed"] is False
        assert report["p159_final_lock"] is False
        assert report["p160_opened"] is False
