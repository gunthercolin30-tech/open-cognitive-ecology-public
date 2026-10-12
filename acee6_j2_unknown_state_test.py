from tempfile import TemporaryDirectory
from pathlib import Path
from acee6_j2_test_support import executor, make_transaction

with TemporaryDirectory() as tmp:
    exe = executor(Path(tmp))
    make_transaction(exe, "tx-j2-unknown", "IMPOSSIBLE_STATE")
    result = exe.escalate_transaction("tx-j2-unknown", persist=True)
    assert result["status"] == "ACEE6_J2_ESCALATION_COMPLETE", result
    assert "transaction_state_unknown:IMPOSSIBLE_STATE" in result["blocking_reasons"]
    assert result["transaction_state"] == "QUARANTINE"
print("ACEE6_J2_UNKNOWN_STATE_OK")
