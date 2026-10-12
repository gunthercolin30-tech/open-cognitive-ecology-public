from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


class InterruptAfterReplace(AceeInstallationExecutor):
    def _copy_backup_atomically(self, *args, **kwargs):
        result = super()._copy_backup_atomically(*args, **kwargs)
        raise RuntimeError("simulated_interruption_after_replace")


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    target = root / "ontology" / "sample_candidate.py"
    target.write_text("before\n", encoding="utf-8")

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
    normalized = admitted["normalized_plan"]
    source = root / normalized["target_path"]
    destination = root / normalized["backup_path"]
    initial_fixture = PreissuedD1Fixture(root, (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ExpectedEffect("FS_COPY2", destination, source),
    ))
    interrupted = False
    try:
        InterruptAfterReplace(
            root=root,
            now_utc=fixed_now(),
            filesystem_effect_context_provider=initial_fixture,
        ).step(inputs=inputs, persist=True)
    except RuntimeError as exc:
        assert str(exc) == "simulated_interruption_after_replace"
        interrupted = True
    assert interrupted, "expected_interruption_not_raised"
    initial_fixture.assert_exhausted()
    assert destination.is_file(), "backup_missing_after_interruption"

    recovery_fixture = PreissuedD1Fixture(root, (
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ExpectedEffect("FS_COPY2", destination, source),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "backup_manifest.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
    ))
    recovered = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
        filesystem_effect_context_provider=recovery_fixture,
    ).step(inputs=inputs, persist=True)
    recovery_fixture.assert_exhausted()

    assert recovered["transaction_state"] == "BACKED_UP"
    assert recovered["candidate_written"] is False

print("ACEE6_D1_INTERRUPT_AFTER_REPLACE_OK")
