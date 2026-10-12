from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ontology.occ_reproducibility_persistence import (
    NormativeLifecycleJournal,
    atomic_write_json,
    clock_integrity,
    make_envelope,
    persistence_report,
    reconcile_state,
    reproducibility_report,
    restart_guard,
    verify_build_completeness,
    verify_envelope,
)


class OCC1JReproducibilityPersistenceTests(unittest.TestCase):
    def test_metadata_does_not_change_semantic_hash(self):
        payload = {"state": "UNKNOWN", "unicode": "éthique", "value": 7}
        a = make_envelope(payload, {"run_id": "A", "timestamp": "2026-01-01T00:00:00Z"})
        b = make_envelope(payload, {"run_id": "B", "timestamp": "2026-09-30T00:00:00Z"})
        self.assertEqual(a["semantic_hash"], b["semantic_hash"])
        self.assertNotEqual(a["artifact_hash"], b["artifact_hash"])
        self.assertEqual(verify_envelope(a)["status"], "PASS")

    def test_unknown_survives_json_roundtrip(self):
        payload = {"semantic_status": "UNKNOWN", "nested": {"status": "CONTESTED"}}
        envelope = make_envelope(payload, {})
        restored = json.loads(json.dumps(envelope, ensure_ascii=False))
        self.assertEqual(restored["CANONICAL_PAYLOAD"]["semantic_status"], "UNKNOWN")
        self.assertEqual(restored["CANONICAL_PAYLOAD"]["nested"]["status"], "CONTESTED")
        self.assertEqual(verify_envelope(restored)["status"], "PASS")

    def test_atomic_write_leaves_no_tmp_and_preserves_exact_payload(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sealed" / "artifact.json"
            payload = {"semantic_status": "UNKNOWN", "authorized": False}
            atomic_write_json(p, payload)
            self.assertEqual(json.loads(p.read_text(encoding="utf-8")), payload)
            self.assertEqual(list(p.parent.glob("*.tmp")), [])

    def test_build_incomplete_and_contamination_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.json").write_text("{}", encoding="utf-8")
            r = verify_build_completeness(root, ["a.json", "b.json"])
            self.assertEqual(r["reason"], "BUILD_INCOMPLETE")
            r = verify_build_completeness(root, ["a.json"], ["a.json", "rogue.json"])
            self.assertEqual(r["reason"], "BUILD_CONTAMINATION")

    def test_journal_chain_and_reconciliation_survive_restart(self):
        with tempfile.TemporaryDirectory() as td:
            journal = NormativeLifecycleJournal(Path(td) / "journal.jsonl")
            e1 = journal.append(
                "PROFILE_BUILT", "abc", state="UNVERIFIED_COMPILED_PROFILE",
                timestamp_utc="2026-09-30T00:00:00Z",
            )
            self.assertEqual(e1["status"], "PASS")
            e2 = journal.append(
                "VERIFIED", "abc", state="VERIFIED",
                timestamp_utc="2026-09-30T00:01:00Z",
            )
            self.assertEqual(e2["status"], "PASS")
            reloaded = NormativeLifecycleJournal(Path(td) / "journal.jsonl")
            check = reloaded.verify()
            self.assertEqual(check["status"], "PASS")
            snapshot = {
                "profile_semantic_hash": "abc",
                "profile_state": "VERIFIED",
                "last_event_hash": check["last_event_hash"],
            }
            self.assertEqual(reconcile_state(snapshot, reloaded)["status"], "PASS")

    def test_journal_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "journal.jsonl"
            journal = NormativeLifecycleJournal(p)
            journal.append(
                "PROFILE_BUILT", "abc", state="UNVERIFIED_COMPILED_PROFILE",
                timestamp_utc="2026-09-30T00:00:00Z",
            )
            obj = json.loads(p.read_text(encoding="utf-8").strip())
            obj["state"] = "ACTIVATED"
            p.write_text(json.dumps(obj) + "\n", encoding="utf-8")
            self.assertEqual(journal.verify()["reason"], "JOURNAL_EVENT_HASH_INVALID")

    def test_restart_cannot_manufacture_authority(self):
        ok = restart_guard({
            "authorization_created": False,
            "authority_created": False,
            "execution_performed": False,
            "pending_authorization": True,
            "authorized": False,
        })
        self.assertEqual(ok["status"], "PASS")
        bad = restart_guard({"p159_final_lock": True})
        self.assertEqual(bad["reason"], "RESTART_AUTHORITY_BOUNDARY_VIOLATION")

    def test_clock_rollback_is_inconclusive_not_pass(self):
        result = clock_integrity(
            "2026-09-30T10:00:00Z", "2026-09-30T09:59:00Z", tolerance_seconds=1
        )
        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["reason"], "CLOCK_INTEGRITY_UNCERTAIN")

    def test_reports_are_separate_and_non_authorizing(self):
        payload = {"semantic_status": "UNKNOWN", "authorized": False}
        a = make_envelope(payload, {"run_id": "1"})
        b = make_envelope(payload, {"run_id": "2"})
        rr = reproducibility_report(a, b, {"build_identity_hash": "build"})
        pr = persistence_report(payload, dict(payload), {"status": "PASS"})
        self.assertEqual(rr["schema"], "oce.p159.occ1j.reproducibility_report.v1")
        self.assertEqual(pr["schema"], "oce.p159.occ1j.persistence_report.v1")
        self.assertEqual(rr["status"], "PASS")
        self.assertEqual(pr["status"], "PASS")
        self.assertFalse(rr["p159_final_lock"])
        self.assertFalse(pr["p160_opened"])


if __name__ == "__main__":
    unittest.main()
