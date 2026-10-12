from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture
    inputs = {"acee5_decision": valid_acee5_decision(root), "admission_context": {"requested_stage": "ACEE6-D1"}}
    dry = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    admitted = dry.step(inputs=inputs, persist=False)
    assert admitted.get("admissible") is True, "final_lock_admission_precondition"
    txdir = root / "acee6_transactions" / dry._transaction_id(admitted)
    fixture = PreissuedD1Fixture(root, (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "backup_manifest.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
    ))
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now(), filesystem_effect_context_provider=fixture).step(inputs=inputs, persist=True)
    fixture.assert_exhausted()
    assert result["stage"] == "ACEE6-D1"
    assert result["public_schema_version"] == "0.5.0"
    assert result["status"] == "ACEE6_TRANSACTION_BACKUP_COMPLETE"
    assert result["transaction_state"] == "BACKED_UP"
    assert result["candidate_written"] is False
    assert result["inventory_modified"] is False
    assert result["tests_executed"] is False
print("ACEE6_D1_BACKUP_FINAL_LOCK_OK")
