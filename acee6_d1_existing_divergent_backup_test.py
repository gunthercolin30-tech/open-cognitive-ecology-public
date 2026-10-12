from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


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

    backup = root / decision["installation_manifest"]["backup_path"]
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text("divergent-existing-backup\n", encoding="utf-8")

    from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture
    dry = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    admitted = dry.step(inputs=inputs, persist=False)
    assert admitted.get("admissible") is True, "d1_degradation_admission_precondition"
    txdir = root / "acee6_transactions" / dry._transaction_id(admitted)
    # The expected divergent/symlink backup is rejected before a copy effect.
    # Rejection returns immediately after acquiring the backup lock.
    # Do not preissue a final state write that cannot be consumed.
    effects = (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
    )
    fixture = PreissuedD1Fixture(root, effects)
    result = AceeInstallationExecutor(
        root=root, now_utc=fixed_now(), filesystem_effect_context_provider=fixture,
    ).step(inputs=inputs, persist=True)
    fixture.assert_exhausted()

    assert result.get("admissible") is False or result.get("transaction_state") in {"PREPARED", "STATE_CORRUPTED"}
    assert "existing_backup_file_hash_divergence" in result["blocking_reasons"]
    assert backup.read_text(encoding="utf-8") == "divergent-existing-backup\n"

print("ACEE6_D1_EXISTING_DIVERGENT_BACKUP_OK")
