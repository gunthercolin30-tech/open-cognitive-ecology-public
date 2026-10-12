from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(
        inputs=valid_acee5_decision(root),
        persist=False,
    )

    assert result["primitive"] == "ACEE_INSTALLATION_EXECUTOR"
    assert result["status"] == "ACEE6_INSTALLATION_PLAN_ADMISSIBLE"
    assert result["dry_run_status"] == "ACEE6_INSTALLATION_DRY_RUN_READY"
    assert result["admissible"] is True
    assert result["dry_run"] is True
    assert result["read_only"] is True
    assert result["write_count"] == 0
    assert result["persistence_performed"] is False
    assert result["candidate_written"] is False
    assert result["inventory_modified"] is False
    assert result["tests_executed"] is False
    assert result["global_validation_executed"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True

print("ACEE6_B2_DRY_RUN_FINAL_LOCK_OK")
