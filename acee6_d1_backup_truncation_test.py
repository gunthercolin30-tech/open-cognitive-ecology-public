from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    target = root / "ontology" / "sample_candidate.py"
    target.write_text("original-backup-content\n", encoding="utf-8")

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
    fixture = PreissuedD1Fixture(root, (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ExpectedEffect("FS_COPY2", root / normalized["backup_path"], root / normalized["target_path"]),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "backup_manifest.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
    ))
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now(), filesystem_effect_context_provider=fixture)
    first = executor.step(inputs=inputs, persist=True)
    fixture.assert_exhausted()

    assert first["transaction_state"] == "BACKED_UP"
    assert first["backup_complete"] is True
    assert first["backup_hash_verified"] is True

    backup = root / first["backup_path"]
    assert backup.is_file()
    backup.write_bytes(b"truncated")

    second = executor.step(inputs=inputs, persist=True)

    assert second["status"] == "ACEE6_TRANSACTION_BACKUP_REJECTED"
    assert second["transaction_state"] == "STATE_CORRUPTED"
    assert second["backup_complete"] is False
    assert "existing_backup_file_hash_divergence" in (
        second["blocking_reasons"]
    )
    assert second["candidate_written"] is False
    assert backup.read_bytes() == b"truncated"

print("ACEE6_D1_BACKUP_TRUNCATION_OK")
