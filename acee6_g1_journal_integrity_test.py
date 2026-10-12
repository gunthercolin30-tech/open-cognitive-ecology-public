from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_installation_executor import AceeInstallationExecutor
from acee6_b1_test_support import fixed_now
from acee6_e_test_support import seed
from acee6_f2_test_support import payload as f2_payload


def canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def main() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        seed(root)
        inputs = f2_payload(root)
        context = dict(inputs["admission_context"])
        context["requested_stage"] = "ACEE6-F2"
        context["fault_injection"] = {
            "enabled": True,
            "point": "report",
            "occurrence": 1,
        }
        inputs["admission_context"] = context

        result = AceeInstallationExecutor(
            root=root,
            now_utc=fixed_now(),
        ).step(inputs=inputs, persist=True)

        assert result.get("status") == "ACEE6_G1_FAULT_INJECTION_TRIGGERED", result
        transaction_id = result.get("transaction_id")
        assert isinstance(transaction_id, str) and transaction_id, result

        tx = root / "acee6_transactions" / transaction_id
        journal_path = tx / "journal.jsonl"
        latest_path = tx / "latest_state.json"
        report_path = tx / "fault_injection_report.json"
        assert journal_path.is_file()
        assert latest_path.is_file()
        assert report_path.is_file()

        records = [
            json.loads(line)
            for line in journal_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert records

        previous = None
        for record in records:
            supplied = record["record_hash"]
            body = dict(record)
            body.pop("record_hash")
            assert body.get("previous_record_hash") == previous
            assert supplied == sha(body)
            previous = supplied

        assert records[-1].get("state") == "FAULT_INJECTED"
        assert records[-1].get("fault_point") == "report"

        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        assert latest.get("latest_record_hash") == previous
        assert latest.get("transaction_state") == "FAULT_INJECTED"
        assert latest.get("committed") is False
        latest_hash = latest["state_hash"]
        latest_body = dict(latest)
        latest_body.pop("state_hash")
        assert latest_hash == sha(latest_body)

        report = json.loads(report_path.read_text(encoding="utf-8"))
        report_hash = report["fault_injection_report_hash"]
        report_body = dict(report)
        report_body.pop("fault_injection_report_hash")
        assert report_hash == sha(report_body)
        assert report.get("transaction_id") == transaction_id
        assert report.get("fault_point") == "report"

    print("ACEE6_G1_JOURNAL_INTEGRITY_OK")


if __name__ == "__main__":
    main()
