from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha


def executor(root: Path) -> AceeInstallationExecutor:
    return AceeInstallationExecutor(root=root, now_utc=datetime(2026, 7, 16, tzinfo=timezone.utc))


def make_transaction(executor: AceeInstallationExecutor, transaction_id: str, state: str, *, rollback_executed=False, rollback_verified=False):
    tx = executor._transaction_runtime_root() / transaction_id
    tx.mkdir(parents=True, exist_ok=True)
    record_hash = executor._append_journal_record(tx / "journal.jsonl", {
        "transaction_id": transaction_id,
        "proposal_id": "proposal-j2",
        "state": state,
        "timestamp_utc": executor.now_utc.isoformat(),
    }, None)
    latest = {
        "primitive": "ACEE_INSTALLATION_EXECUTOR",
        "transaction_id": transaction_id,
        "proposal_id": "proposal-j2",
        "manifest_hash": "a" * 64,
        "plan_hash": "b" * 64,
        "transaction_state": state,
        "latest_record_hash": record_hash,
        "rollback_executed": rollback_executed,
        "rollback_verified": rollback_verified,
        "quarantined": state == "QUARANTINE",
        "timestamp_utc": executor.now_utc.isoformat(),
    }
    latest["state_hash"] = _sha(latest)
    executor._atomic_json_write(tx / "latest_state.json", latest)
    return tx
