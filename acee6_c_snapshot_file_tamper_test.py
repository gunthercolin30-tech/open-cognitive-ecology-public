import json
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    first = executor.step(inputs=decision, persist=True)
    snapshot = Path(first["snapshot_path"])
    payload = json.loads(snapshot.read_text(encoding="utf-8"))
    payload["entries"][0]["size"] = 999999
    snapshot.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    second = executor.step(inputs=decision, persist=True)
    assert second["transaction_prepared"] is False
    assert "existing_transaction_snapshot_hash_mismatch" in second["blocking_reasons"]
print("ACEE6_C_SNAPSHOT_FILE_TAMPER_OK")
