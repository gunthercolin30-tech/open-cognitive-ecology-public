from tempfile import TemporaryDirectory
from pathlib import Path
from acee6_j2_test_support import executor, make_transaction

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    exe = executor(root)
    make_transaction(exe, "tx-j2-committed", "COMMITTED", rollback_executed=False, rollback_verified=False)
    result = exe.escalate_transaction("tx-j2-committed", persist=True)
    assert result["status"] == "ACEE6_J2_ESCALATION_NOT_REQUIRED", result
    assert result["escalation_required"] is False
    assert result["persistence_performed"] is False
    assert not exe._j2_gate_path().exists()
    gate = exe.inspect_escalation_gate()
    assert gate["installation_blocked"] is False
print("ACEE6_J2_NON_REGRESSION_OK")
