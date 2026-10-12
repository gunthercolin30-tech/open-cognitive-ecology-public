import fcntl
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    decision = valid_acee5_decision(root)
    inputs = {
        "acee5_decision": decision,
        "admission_context": {"requested_stage": "ACEE6-D1"},
    }

    from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture
    dry = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    admitted = dry.step(inputs=inputs, persist=False)
    assert admitted.get("admissible") is True
    txdir = root / "acee6_transactions" / dry._transaction_id(admitted)
    fixture = PreissuedD1Fixture(root, (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "backup_manifest.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
    ))
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now(), filesystem_effect_context_provider=fixture)
    prepared = executor.step(inputs=inputs, persist=True)
    fixture.assert_exhausted()
    transaction_dir = Path(prepared["transaction_directory"])
    lock_path = root / "acee6_transactions" / ".backup.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        blocked = executor.step(inputs=inputs, persist=True)
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    assert blocked["transaction_state"] in {"PREPARED", "BACKED_UP"}
    if blocked["transaction_state"] == "PREPARED":
        assert blocked["status"] == "ACEE6_TRANSACTION_BACKUP_BLOCKED"
        assert "transaction_backup_lock_busy" in blocked["blocking_reasons"]
    assert blocked["candidate_written"] is False

print("ACEE6_D1_BACKUP_LOCK_COLLISION_OK")
