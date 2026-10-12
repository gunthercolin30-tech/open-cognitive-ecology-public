from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    b2 = executor.step(inputs=decision, persist=False)
    from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture
    admitted = executor.step(inputs=decision, persist=False)
    assert admitted.get("admissible") is True, "d1_non_regression_admission_precondition"
    txdir = root / "acee6_transactions" / executor._transaction_id(admitted)
    fixture = PreissuedD1Fixture(root, (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
    ))
    governed = AceeInstallationExecutor(root=root, now_utc=fixed_now(), filesystem_effect_context_provider=fixture)
    c = governed.step(inputs=decision, persist=True)
    fixture.assert_exhausted()
    assert b2["dry_run"] is True and b2["write_count"] == 0
    assert c["transaction_state"] == "PREPARED"
    assert c["backup_created"] is False
print("ACEE6_D1_NON_REGRESSION_OK")
