from tempfile import TemporaryDirectory
from pathlib import Path
from acee6_j2_test_support import executor, make_transaction

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    exe = executor(root)
    make_transaction(exe, "tx-j2-functional", "QUARANTINE", rollback_executed=False, rollback_verified=False)
    result = exe.escalate_transaction("tx-j2-functional", persist=True)
    assert result["status"] == "ACEE6_J2_ESCALATION_COMPLETE", result
    assert result["installation_blocked"] is True
    assert result["retry_allowed"] is False
    assert Path(result["diagnostic_path"]).is_file()
    assert Path(result["gate_path"]).is_file()
    blocked = exe.step(inputs={}, persist=False)
    assert blocked["status"] == "ACEE6_J2_INSTALLATION_BLOCKED", blocked
    assert blocked["admissible"] is False
    assert blocked["candidate_executed"] is False
print("ACEE6_J2_FUNCTIONAL_OK")
