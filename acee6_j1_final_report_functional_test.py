from __future__ import annotations
import hashlib, json, tempfile
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor

def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

def seed_transaction(root: Path, tamper_global: bool = False) -> str:
    tx = "tx-j1"
    directory = root / "acee6_transactions" / tx
    directory.mkdir(parents=True)
    record = {"transaction_id": tx, "proposal_id": "proposal-j1", "state": "GLOBAL_VALIDATED", "timestamp_utc": "2026-07-16T12:00:00+00:00", "previous_record_hash": None}
    record["record_hash"] = sha(record)
    (directory / "journal.jsonl").write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    latest = {"transaction_id": tx, "proposal_id": "proposal-j1", "manifest_hash": "a" * 64, "plan_hash": "b" * 64, "transaction_state": "GLOBAL_VALIDATED", "latest_record_hash": record["record_hash"], "tests_executed": True, "global_validation_executed": True, "rollback_executed": False}
    latest["state_hash"] = sha(latest)
    write_json(directory / "latest_state.json", latest)
    local = {"transaction_id": tx, "proposal_id": "proposal-j1", "validation_complete": True, "validation_passed": True, "error_count": 0, "failed_commands": [], "timed_out_commands": [], "blocked_commands": [], "local_duration_seconds": 1.25}
    local["local_validation_report_hash"] = sha(local)
    write_json(directory / "local_validation_report.json", local)
    global_report = {"transaction_id": tx, "proposal_id": "proposal-j1", "validation_complete": True, "validation_passed": True, "error_count": 0, "failed_calls": 0, "failed_modules": [], "global_duration_seconds": 15.477}
    global_report["global_validation_report_hash"] = sha(global_report)
    if tamper_global:
        global_report["error_count"] = 99
    write_json(directory / "global_validation_report.json", global_report)
    compilation = {"transaction_id": tx, "compilation_duration_ns": 123456}
    compilation["compilation_report_hash"] = sha(compilation)
    write_json(directory / "compilation_report.json", compilation)
    return tx

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    tx = seed_transaction(root)
    result = AceeInstallationExecutor(root=root).build_final_report(tx)
    assert result["status"] == "ACEE6_FINAL_REPORT_COMPLETE", result
    assert result["report_complete"] is True
    assert result["hashes"]["evidence_manifest_hash"]
    assert result["tests"]["error_count"] == 0
    assert result["validation"]["failed_calls"] == 0
    assert result["durations"], result
    assert result["proofs"]["journal_chain_valid"] is True
    assert result["persistence_performed"] is False
print("ACEE6_J1_FINAL_REPORT_FUNCTIONAL_OK")
