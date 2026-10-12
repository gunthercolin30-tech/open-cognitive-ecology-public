#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

def atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")

def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        tx = root / "acee6_transactions" / "tx-prepared"
        tx.mkdir(parents=True)
        record = {"transaction_id":"tx-prepared","proposal_id":"p1","state":"PREPARED","timestamp_utc":"2026-07-16T00:00:00+00:00","previous_record_hash":None}
        record["record_hash"] = _sha(record)
        (tx / "journal.jsonl").write_text(json.dumps(record, sort_keys=True)+"\n", encoding="utf-8")
        latest = {"transaction_id":"tx-prepared","proposal_id":"p1","transaction_state":"PREPARED","latest_record_hash":record["record_hash"]}
        latest["state_hash"] = _sha(latest)
        atomic(tx / "latest_state.json", latest)
        engine = AceeInstallationExecutor(root=root, now_utc=datetime(2026,7,16,tzinfo=timezone.utc))
        result = engine.recover_transaction("tx-prepared", persist=False)
        assert result["status"] == "ACEE6_CRASH_RECOVERY_COMPLETE", result
        assert result["crash_recovery_action"] == "resume_safe", result
        assert result["transaction_state"] == "PREPARED", result
        assert result["persistence_performed"] is False, result
        print("ACEE6_I1_FUNCTIONAL_OK")
if __name__ == "__main__": main()
