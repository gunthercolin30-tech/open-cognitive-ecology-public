import json
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    first = executor.step(inputs=decision, persist=True)
    latest = Path(first["latest_state_path"])
    payload = json.loads(latest.read_text(encoding="utf-8"))
    payload["latest_record_hash"] = "a" * 64
    payload["state_hash"] = _sha({k: v for k, v in payload.items() if k != "state_hash"})
    latest.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    second = executor.step(inputs=decision, persist=True)
    assert second["transaction_prepared"] is False
    assert "existing_transaction_latest_record_divergence" in second["blocking_reasons"]
print("ACEE6_C_LATEST_RECORD_DIVERGENCE_OK")
