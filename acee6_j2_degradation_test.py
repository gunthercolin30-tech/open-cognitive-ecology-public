import json
from tempfile import TemporaryDirectory
from pathlib import Path
from acee6_j2_test_support import executor, make_transaction

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    exe = executor(root)
    tx = make_transaction(exe, "tx-j2-corrupt", "PREPARED")
    (tx / "journal.jsonl").write_text("{corrupt journal\n", encoding="utf-8")
    preview = exe.escalate_transaction("tx-j2-corrupt", persist=False)
    assert preview["escalation_required"] is True, preview
    assert preview["persistence_performed"] is False
    assert not exe._j2_gate_path().exists()
    persisted = exe.escalate_transaction("tx-j2-corrupt", persist=True)
    assert "journal_json_invalid:0" in persisted["blocking_reasons"], persisted
    gate_path = exe._j2_gate_path()
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    gate["transaction_id"] = "tampered"
    gate_path.write_text(json.dumps(gate), encoding="utf-8")
    inspected = exe.inspect_escalation_gate()
    assert inspected["installation_blocked"] is True
    assert inspected["gate_integrity_verified"] is False
    assert "escalation_gate_corrupted" in inspected["blocking_reasons"]
print("ACEE6_J2_DEGRADATION_OK")
