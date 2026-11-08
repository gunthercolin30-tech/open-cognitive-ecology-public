"""PC4 recovery invariants using disposable journals, without issued authority."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "p162_recovery_under_test", ROOT / "ontology/reservation_recovery_manager.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def record(**changes):
    body = {"type": "RESERVATION_COMMITTED", "reservation_id": "r",
            "seq": 1, "prev_hash": "GENESIS", **changes}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {**body, "event_hash": hashlib.sha256(raw.encode()).hexdigest()}


class RecoveryHardeningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="p162-pc4-recovery-test-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "journal.jsonl"
        self.journal = MODULE.ReservationRecoveryJournal(self.path)

    def event(self, kind, **extra):
        return self.journal.append({"type": kind, "reservation_id": "r", **extra})

    def assert_unknown(self):
        self.assertEqual(self.journal.replay()["status"], "INDETERMINATE")
        value = self.journal.idempotent_recover("r", effect_evidence={})
        self.assertEqual(value["state"], "INDETERMINATE")
        self.assertIs(value["replay_permitted"], False)
        self.assertIs(value["automatic_resume_allowed"], False)
        self.assertIs(value["authorization_created"], False)

    def test_valid_history_replays_and_confirmed_effect_stays_consumed(self):
        for kind in ("RESERVATION_COMMITTED", "EXECUTION_STARTED", "EXECUTION_CONFIRMED"):
            self.event(kind)
        self.assertEqual(len(self.journal.replay()["events"]), 3)
        self.assertEqual(self.journal.reconstruct("r")["state"], "CONSUMED")
        self.assertEqual(self.journal.reconstruct("r")["assessment"], "CONFIRMED_USED")

    def test_late_commit_or_start_cannot_resurrect_consumed_reservation(self):
        self.event("EXECUTION_CONFIRMED")
        for kind in ("RESERVATION_COMMITTED", "EXECUTION_STARTED", "CONFIRMED_UNUSED"):
            self.event(kind)
            value = self.journal.reconstruct("r")
            self.assertEqual(value["state"], "CONSUMED")
            self.assertEqual(value["assessment"], "CONFIRMED_USED")

    def test_indeterminate_history_never_becomes_reserved_or_consumed(self):
        self.event("EFFECT_INDETERMINATE")
        for kind in ("RESERVATION_COMMITTED", "EXECUTION_STARTED", "EXECUTION_CONFIRMED"):
            self.event(kind)
            self.assertEqual(self.journal.reconstruct("r")["state"], "INDETERMINATE")

    def test_non_object_json_is_unknown_without_exception(self):
        for value in (None, [], 1, "scalar", True):
            with self.subTest(value=value):
                self.path.write_text(json.dumps(value) + "\n")
                self.assert_unknown()

    def test_truncated_record_is_unknown(self):
        self.event("RESERVATION_COMMITTED")
        self.path.write_bytes(self.path.read_bytes().rstrip(b"\n"))
        self.assert_unknown()

    def test_duplicate_json_keys_are_unknown_even_with_matching_last_value_hash(self):
        value = record()
        raw = json.dumps(value).replace('"seq": 1', '"seq": 0, "seq": 1')
        self.path.write_text(raw + "\n")
        self.assert_unknown()

    def test_non_finite_json_is_unknown(self):
        self.path.write_text(json.dumps(record(measurement=float("nan"))) + "\n")
        self.assert_unknown()

    def test_boolean_sequence_is_not_integer_sequence(self):
        self.path.write_text(json.dumps(record(seq=True)) + "\n")
        self.assert_unknown()

    def test_invalid_utf8_is_unknown(self):
        self.path.write_bytes(b"\xff\n")
        self.assert_unknown()

    def test_unreadable_journal_is_unknown(self):
        with patch.object(MODULE.os, "open", side_effect=PermissionError("synthetic")):
            self.assert_unknown()

    def test_existing_directory_is_unknown(self):
        self.path.mkdir()
        with patch.object(MODULE.os, "close", wraps=MODULE.os.close) as close:
            self.assert_unknown()
        self.assertEqual(close.call_count, 2)

    def test_dangling_symlink_is_not_missing_journal(self):
        self.path.symlink_to(Path(self.temp.name) / "missing")
        self.assert_unknown()

    def test_invalid_backup_is_conservative(self):
        self.event("RESERVATION_COMMITTED")
        for backup in ([], "bad", {}, {"state": "UNRECOGNIZED"}, {"state": []}):
            with self.subTest(backup=backup):
                self.assertEqual(self.journal.reconstruct("r", backup)["state"], "INDETERMINATE")

    def test_caller_cannot_override_chain_metadata(self):
        for field, value in (("seq", 1), ("prev_hash", "GENESIS"), ("event_hash", "x")):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    self.event("RESERVATION_COMMITTED", **{field: value})
                self.assertFalse(self.path.exists())

    def test_corrupt_journal_append_is_refused_without_write(self):
        self.path.write_text("null\n")
        original = self.path.read_bytes()
        with self.assertRaises(RuntimeError):
            self.event("RESERVATION_COMMITTED")
        self.assertEqual(self.path.read_bytes(), original)

    def test_governed_append_uses_existing_context_and_blocks_corruption(self):
        calls = []
        path = self.path
        class Context:
            def execute_path(self, slot, operation, target, payload):
                calls.append((slot, operation, target))
                target.write_bytes(payload)  # Disposable test transport only.
        event = {"type": "RESERVATION_COMMITTED", "reservation_id": "r"}
        self.journal.append_governed(event, Context())
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.journal.replay()["status"], "OK")
        self.path.write_text("[]\n")
        with self.assertRaises(RuntimeError):
            self.journal.append_governed(event, Context())
        self.assertEqual(len(calls), 1)

    def test_empty_missing_journal_does_not_enable_resume(self):
        value = self.journal.idempotent_recover("r", effect_evidence={})
        self.assertIs(value["replay_permitted"], False)
        self.assertIs(value["automatic_resume_allowed"], False)


if __name__ == "__main__":
    unittest.main()
