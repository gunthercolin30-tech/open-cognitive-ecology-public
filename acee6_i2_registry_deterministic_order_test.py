from __future__ import annotations
import hashlib, json, multiprocessing as mp, tempfile
from pathlib import Path
from typing import Any
from ontology.acee_installation_executor import AceeInstallationExecutor

def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

def make_transaction(root: Path, transaction_id: str, proposal_id: str, manifest_hash: str, plan_hash: str = "1"*64, state: str = "PREPARED") -> Path:
    directory = root / "acee6_transactions" / transaction_id
    directory.mkdir(parents=True, exist_ok=True)
    record = {"transaction_id": transaction_id, "proposal_id": proposal_id, "manifest_hash": manifest_hash, "plan_hash": plan_hash, "state": state, "previous_record_hash": None}
    record["record_hash"] = canonical_hash(record)
    (directory / "journal.jsonl").write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    latest = {"transaction_id": transaction_id, "proposal_id": proposal_id, "manifest_hash": manifest_hash, "plan_hash": plan_hash, "transaction_state": state, "latest_record_hash": record["record_hash"]}
    latest["state_hash"] = canonical_hash(latest)
    (directory / "latest_state.json").write_text(json.dumps(latest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return directory

def snapshot_tree(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    for tx, proposal, manifest in [("tx-z","proposal-b","c"*64),("tx-a","proposal-a","a"*64),("tx-m","proposal-b","b"*64)]:
        make_transaction(root, tx, proposal, manifest)
    first = AceeInstallationExecutor(root=root).inspect_replay_registry()
    second = AceeInstallationExecutor(root=root).inspect_replay_registry()
    assert list(first["proposal_collisions"]) == sorted(first["proposal_collisions"]), first
    identities = first["proposal_collisions"]["proposal-b"]
    assert [item["transaction_id"] for item in identities] == ["tx-m","tx-z"], identities
    a, b = dict(first), dict(second)
    a.pop("result_hash", None); b.pop("result_hash", None)
    assert a == b, (a, b)
print("ACEE6_I2_REGISTRY_DETERMINISTIC_ORDER_OK")
