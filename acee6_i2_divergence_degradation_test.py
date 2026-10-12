from __future__ import annotations
import hashlib, json, tempfile
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor

def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

def make_transaction(root: Path, tx: str, proposal: str, manifest: str, state: str = "PREPARED"):
    directory = root / "acee6_transactions" / tx
    directory.mkdir(parents=True, exist_ok=True)
    record = {"transaction_id": tx, "proposal_id": proposal, "manifest_hash": manifest, "plan_hash": "1" * 64, "state": state, "previous_record_hash": None}
    record["record_hash"] = sha(record)
    (directory / "journal.jsonl").write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    latest = {"transaction_id": tx, "proposal_id": proposal, "manifest_hash": manifest, "plan_hash": "1" * 64, "transaction_state": state, "latest_record_hash": record["record_hash"]}
    latest["state_hash"] = sha(latest)
    (directory / "latest_state.json").write_text(json.dumps(latest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return directory

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp); directory = make_transaction(root, "tx-a", "proposal-a", "a" * 64)
    latest = json.loads((directory / "latest_state.json").read_text())
    latest["latest_record_hash"] = "f" * 64
    latest["state_hash"] = sha({k:v for k,v in latest.items() if k != "state_hash"})
    (directory / "latest_state.json").write_text(json.dumps(latest))
    result = AceeInstallationExecutor(root=root).inspect_replay("tx-a", "proposal-a", "a" * 64)
    assert result["status"] == "ACEE6_REPLAY_REJECTED", result
    assert result["replay_classification"] == "state_divergence"
print("ACEE6_I2_DIVERGENCE_DEGRADATION_OK")
