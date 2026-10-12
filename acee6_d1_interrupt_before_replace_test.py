from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


class InterruptBeforeReplace(AceeInstallationExecutor):
    def _copy_backup_atomically(self, *args, **kwargs):
        raise RuntimeError("simulated_interruption_before_replace")


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

    try:
        from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture
        dry = AceeInstallationExecutor(root=root, now_utc=fixed_now())
        admitted = dry.step(inputs=inputs, persist=False)
        assert admitted.get("admissible") is True
        txdir = root / "acee6_transactions" / dry._transaction_id(admitted)
        fixture = PreissuedD1Fixture(root, (
            ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
            ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
            ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ))
        try:
            InterruptBeforeReplace(
                root=root,
                now_utc=fixed_now(),
                filesystem_effect_context_provider=fixture,
            ).step(inputs=inputs, persist=True)
        finally:
            fixture.assert_exhausted()
    except RuntimeError as exc:
        assert str(exc) == "simulated_interruption_before_replace"

    backup_path = root / decision["installation_manifest"]["backup_path"]
    assert not backup_path.exists()
    assert target.read_text(encoding="utf-8") == "before\n"

print("ACEE6_D1_INTERRUPT_BEFORE_REPLACE_OK")
