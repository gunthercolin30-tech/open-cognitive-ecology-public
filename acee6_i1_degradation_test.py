#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp); tx = root / "acee6_transactions" / "tx-corrupt"; tx.mkdir(parents=True)
        record = {"transaction_id":"tx-corrupt","state":"PREPARED","timestamp_utc":"2026-07-16T00:00:00+00:00","previous_record_hash":None}
        record["record_hash"] = "0" * 64
        (tx / "journal.jsonl").write_text(json.dumps(record)+"\n", encoding="utf-8")
        latest = {"transaction_id":"tx-corrupt","transaction_state":"PREPARED","latest_record_hash":record["record_hash"]}
        latest["state_hash"] = _sha(latest)
        (tx / "latest_state.json").write_text(json.dumps(latest)+"\n", encoding="utf-8")
        engine = AceeInstallationExecutor(root=root, now_utc=datetime(2026,7,16,tzinfo=timezone.utc))
        audit = engine.recover_transaction("tx-corrupt", persist=False)
        assert audit["transaction_state"] == "STATE_CORRUPTED", audit
        assert audit["crash_recovery_action"] == "quarantine_required", audit
        persisted = engine.recover_transaction("tx-corrupt", persist=True)
        assert persisted["transaction_state"] == "QUARANTINE", persisted
        assert persisted["partial_success"] is False, persisted
        print("ACEE6_I1_DEGRADATION_OK")
if __name__ == "__main__": main()
