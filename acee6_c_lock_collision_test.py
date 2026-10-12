import fcntl
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    runtime = root / "acee6_transactions"
    runtime.mkdir()
    lock_path = runtime / ".prepare.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
            inputs=valid_acee5_decision(root), persist=True
        )
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    assert result["status"] == "ACEE6_TRANSACTION_PREPARATION_BLOCKED"
    assert result["lock_acquired"] is False
    assert "transaction_prepare_lock_busy" in result["blocking_reasons"]
print("ACEE6_C_LOCK_COLLISION_OK")
