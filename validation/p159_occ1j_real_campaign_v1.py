from __future__ import annotations

import json
from pathlib import Path

from ontology import occ_reproducibility_persistence as rp
from validation.p159_occ1j_real_reproducibility_persistence_v1_test import (
    ROOT, OCC1E, _load, identity, rebuild_real_cnp,
)

OUT = ROOT / "validation_artifacts" / "p159" / "occ1j"


def _write(path: Path, obj: dict) -> None:
    rp.atomic_write_json(path, obj)


def main() -> None:
    reference = _load(OCC1E)
    rebuilt = rebuild_real_cnp()
    ref_env = rp.make_envelope(reference, {"role": "locked_occ1e_reference"})
    rebuilt_env = rp.make_envelope(rebuilt, {"role": "occ1j_clean_rebuild"})
    build_id = identity()

    rr = rp.reproducibility_report(ref_env, rebuilt_env, build_id)

    journal_path = OUT / "normative_lifecycle_journal_v1.jsonl"
    if journal_path.exists():
        journal_path.unlink()
    journal = rp.NormativeLifecycleJournal(journal_path)
    e1 = journal.append(
        "PROFILE_BUILT", rebuilt_env["semantic_hash"],
        state="COMPILED", timestamp_utc="2026-09-30T00:00:00Z",
        details={"authority_created": False, "execution_performed": False},
    )
    if e1["status"] != "PASS":
        raise SystemExit(e1)
    e2 = journal.append(
        "VERIFIED", rebuilt_env["semantic_hash"],
        state="VERIFIED", timestamp_utc="2026-09-30T00:01:00Z",
        details={"authorization_created": False, "p159_final_lock": False, "p160_opened": False},
    )
    if e2["status"] != "PASS":
        raise SystemExit(e2)
    jv = journal.verify()

    persisted_state = {
        "schema": "oce.p159.occ1j.persisted_state.v1",
        "profile_semantic_hash": rebuilt_env["semantic_hash"],
        "profile_state": "VERIFIED",
        "last_event_hash": jv["last_event_hash"],
        "authorization_created": False,
        "authority_created": False,
        "execution_performed": False,
        "pending_authorization": False,
        "authorized": False,
        "p159_final_lock": False,
        "p160_opened": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
    _write(OUT / "persisted_state_v1.json", persisted_state)
    restored = _load(OUT / "persisted_state_v1.json")
    reconcile = rp.reconcile_state(restored, journal)
    restart = rp.restart_guard(restored)
    if reconcile["status"] != "PASS" or restart["status"] != "PASS":
        raise SystemExit({"reconcile": reconcile, "restart": restart})

    pr = rp.persistence_report(persisted_state, restored, jv)

    _write(OUT / "build_identity_v1.json", build_id)
    _write(OUT / "reference_profile_envelope_v1.json", ref_env)
    _write(OUT / "rebuilt_profile_envelope_v1.json", rebuilt_env)
    _write(OUT / "reproducibility_report_v1.json", rr)
    _write(OUT / "persistence_report_v1.json", pr)

    completeness = rp.verify_build_completeness(
        OUT,
        [
            "build_identity_v1.json",
            "reference_profile_envelope_v1.json",
            "rebuilt_profile_envelope_v1.json",
            "reproducibility_report_v1.json",
            "persistence_report_v1.json",
            "persisted_state_v1.json",
            "normative_lifecycle_journal_v1.jsonl",
        ],
    )
    _write(OUT / "build_completeness_report_v1.json", completeness)

    ok = rr["status"] == pr["status"] == completeness["status"] == "PASS"
    print("P159_OCC1J_REAL_REPRODUCIBILITY_OK" if rr["status"] == "PASS" else "P159_OCC1J_REAL_REPRODUCIBILITY_FAIL")
    print("P159_OCC1J_REAL_PERSISTENCE_OK" if pr["status"] == "PASS" else "P159_OCC1J_REAL_PERSISTENCE_FAIL")
    print("P159_OCC1J_BUILD_COMPLETENESS_OK" if completeness["status"] == "PASS" else "P159_OCC1J_BUILD_COMPLETENESS_FAIL")
    print("P159_FINAL_LOCK=false")
    print("P160_OPENED=false")
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
