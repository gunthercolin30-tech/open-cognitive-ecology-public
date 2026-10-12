import os
import stat
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

    from validation.acee6_d1_preissued_fixture import ExpectedEffect, PreissuedD1Fixture

    dry_executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    admitted = dry_executor.step(inputs=inputs, persist=False)
    assert admitted.get("admissible") is True
    txdir = root / "acee6_transactions" / dry_executor._transaction_id(admitted)
    normalized = admitted["normalized_plan"]
    source = root / normalized["target_path"]
    destination = root / normalized["backup_path"]
    fixture = PreissuedD1Fixture(root, (
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "snapshot.json"),
        ExpectedEffect("FS_WRITE_REPLACE_BYTES", txdir / "latest_state.json"),
        ExpectedEffect("FS_CREATE_DIR", root / "acee6_transactions"),
        ExpectedEffect("FS_COPY2", destination, source),
    ))
    original_mode = stat.S_IMODE(backup.parent.stat().st_mode)
    os.chmod(backup.parent, 0o500)
    governed_denial = False
    result = None
    try:
        try:
            result = AceeInstallationExecutor(
                root=root,
                now_utc=fixed_now(),
                filesystem_effect_context_provider=fixture,
            ).step(inputs=inputs, persist=True)
        except RuntimeError as exc:
            # The governed effector wraps the underlying filesystem failure.
            # Accept only this exact fail-closed outcome, not arbitrary errors.
            if str(exc) != (
                "governed_filesystem_effect_not_confirmed:"
                "filesystem_exception_after_dispatch"
            ):
                raise
            governed_denial = True
        fixture.assert_exhausted()
    finally:
        os.chmod(backup.parent, original_mode)

    if os.geteuid() != 0:
        assert governed_denial or (
            result is not None
            and result["transaction_state"] in {"PREPARED", "STATE_CORRUPTED"}
            and any(
                reason in result["blocking_reasons"]
                for reason in ("backup_permission_denied", "backup_write_failed")
            )
        )
    if governed_denial:
        assert not backup.exists(), "denied_copy_created_backup"
    assert target.read_text(encoding="utf-8") == "before\n"

print("ACEE6_D1_PERMISSIONS_FAILURE_OK")
