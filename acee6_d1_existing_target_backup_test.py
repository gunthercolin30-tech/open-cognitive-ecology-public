import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    target = root / "ontology" / "sample_candidate.py"
    target.write_text("original\n", encoding="utf-8")
    backup = Path(str(target) + ".bak")
    backup.write_bytes(target.read_bytes())
    from ontology.acee_installation_executor import _sha
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    decision["installation_manifest"]["backup_sha256"] = actual
    decision["installation_manifest"]["manifest_hash"] = _sha({
        k: v for k, v in decision["installation_manifest"].items()
        if k != "manifest_hash"
    })
    decision["result_hash"] = _sha({
        k: v for k, v in decision.items() if k != "result_hash"
    })
    inputs = {"acee5_decision": decision, "admission_context": {"requested_stage": "ACEE6-D1"}}
    # Preissued, exact FIFO. FS_CREATE_DIR on transaction root is consumed
    # by the executor without executing a path effect; it remains explicit.
    from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture
    dry_executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    admitted = dry_executor.step(inputs=inputs, persist=False)
    assert admitted.get("admissible") is True, "d1_admission_precondition_failed"
    txid = dry_executor._transaction_id(admitted)
    txdir = root / "acee6_transactions" / txid
    normalized = admitted["normalized_plan"]
    source = root / normalized["target_path"]
    destination = root / normalized["backup_path"]
    assert source == target and destination == backup, "d1_backup_plan_divergence"
    assert destination.parent.is_dir(), "d1_backup_parent_precondition_failed"
    expected = (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ExpectedEffect("FS_COPY2", destination, source),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "backup_manifest.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
    )
    fixture = PreissuedD1Fixture(root, expected)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now(), filesystem_effect_context_provider=fixture).step(inputs=inputs, persist=True)
    fixture.assert_exhausted()
    assert result["transaction_state"] == "BACKED_UP"
    assert result["backup_created"] is True
    assert backup.read_bytes() == target.read_bytes()
    assert result["backup_sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
    assert result["candidate_written"] is False
print("ACEE6_D1_EXISTING_TARGET_BACKUP_OK")
