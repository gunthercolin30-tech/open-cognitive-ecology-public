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
    journal = Path(first["journal_path"])
    records = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    records[1]["previous_record_hash"] = "0" * 64
    payload = {k: v for k, v in records[1].items() if k != "record_hash"}
    records[1]["record_hash"] = _sha(payload)
    journal.write_text("\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in records) + "\n", encoding="utf-8")
    second = executor.step(inputs=decision, persist=True)
    assert second["transaction_prepared"] is False
    assert "existing_transaction_journal_chain_divergence" in second["blocking_reasons"]
print("ACEE6_C_JOURNAL_CHAIN_TAMPER_OK")
