from __future__ import annotations
import hashlib
import json
import tempfile
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor

def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

def seed_transaction(root: Path, state: str, *, include_local: bool = True, include_global: bool = True, include_rollback: bool = False, rollback_verified: bool = False) -> str:
    transaction_id = "tx-j1-extended"
    directory = root / "acee6_transactions" / transaction_id
    directory.mkdir(parents=True)
    record = {"transaction_id": transaction_id, "proposal_id": "proposal-j1", "state": state, "timestamp_utc": "2026-07-16T12:00:00+00:00", "previous_record_hash": None}
    record["record_hash"] = sha(record)
    (directory / "journal.jsonl").write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    latest = {"transaction_id": transaction_id, "proposal_id": "proposal-j1", "manifest_hash": "a" * 64, "plan_hash": "b" * 64, "transaction_state": state, "latest_record_hash": record["record_hash"], "tests_executed": include_local, "global_validation_executed": include_global, "rollback_executed": include_rollback, "rollback_verified": rollback_verified}
    latest["state_hash"] = sha(latest)
    write_json(directory / "latest_state.json", latest)
    if include_local:
        local = {"transaction_id": transaction_id, "validation_complete": True, "validation_passed": True, "error_count": 0, "failed_commands": [], "timed_out_commands": [], "blocked_commands": [], "local_duration_seconds": 1.25}
        local["local_validation_report_hash"] = sha(local)
        write_json(directory / "local_validation_report.json", local)
    if include_global:
        global_report = {"transaction_id": transaction_id, "validation_complete": True, "validation_passed": True, "error_count": 0, "failed_calls": 0, "failed_modules": [], "global_duration_seconds": 15.5}
        global_report["global_validation_report_hash"] = sha(global_report)
        write_json(directory / "global_validation_report.json", global_report)
    if include_rollback:
        rollback = {"transaction_id": transaction_id, "rollback_executed": True, "rollback_verified": rollback_verified, "rollback_duration_seconds": 0.75}
        rollback["rollback_report_hash"] = sha(rollback)
        write_json(directory / "rollback_report.json", rollback)
    return transaction_id

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp); tx = seed_transaction(root, "COMMITTED", include_global=False)
    report = AceeInstallationExecutor(root=root).build_final_report(tx)
    assert report["status"] == "ACEE6_FINAL_REPORT_INCOMPLETE", report
    assert "global_validation_report_missing" in report["blocking_reasons"]
print("ACEE6_J1_MISSING_PROOF_DEGRADATION_OK")
