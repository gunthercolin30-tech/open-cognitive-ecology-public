from __future__ import annotations
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload
from ontology.acee_installation_executor import AceeInstallationExecutor


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        target = root / "ontology" / "sample_candidate.py"
        target.write_text("ORIGINAL = 3\n", encoding="utf-8")
        original = target.read_bytes()

        inputs = payload(root)
        context = dict(inputs["admission_context"])
        context["requested_stage"] = "ACEE6-D2"
        context["fault_injection"] = {
            "enabled": True,
            "point": "write",
            "occurrence": 1,
            "execute_rollback": True,
        }
        inputs["admission_context"] = context
        engine = AceeInstallationExecutor(root=root, now_utc=fixed_now())
        first = engine.step(inputs=inputs, persist=True)
        assert first["transaction_state"] == "ROLLED_BACK", first
        assert target.read_bytes() == original

        second = engine._g2_rollback_fault(first)
        assert second["transaction_state"] == "ROLLED_BACK", second
        assert second["rollback_verified"] is True, second
        assert target.read_bytes() == original

        tx = root / "acee6_transactions" / first["transaction_id"]
        report_path = tx / "rollback_report.json"
        latest_path = tx / "latest_state.json"
        journal_path = tx / "journal.jsonl"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        stored = report.pop("rollback_report_hash")
        assert canonical_sha(report) == stored, (stored, canonical_sha(report))
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        state_hash = latest.pop("state_hash")
        assert canonical_sha(latest) == state_hash
        rows = [json.loads(line) for line in journal_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert rows[-1]["state"] == "ROLLED_BACK", rows[-1]
        assert all(row.get("state") != "COMMITTED" for row in rows)
        for index, row in enumerate(rows):
            record_hash = row.get("record_hash")
            payload_row = dict(row)
            payload_row.pop("record_hash", None)
            assert canonical_sha(payload_row) == record_hash, (index, row)
            if index:
                assert row.get("previous_record_hash") == rows[index - 1].get("record_hash"), (index, row)
    print("ACEE6_G2_REPLAY_AND_REPORT_INTEGRITY_OK")


if __name__ == "__main__":
    main()
