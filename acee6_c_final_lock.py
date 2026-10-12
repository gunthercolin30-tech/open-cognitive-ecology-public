from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=valid_acee5_decision(root), persist=True
    )
    assert result["primitive"] == "ACEE_INSTALLATION_EXECUTOR"
    assert result["stage"] == "ACEE6-C"
    assert result["public_schema_version"] == "0.4.0"
    assert result["status"] == "ACEE6_TRANSACTION_PREPARED"
    assert result["transaction_state"] == "PREPARED"
    assert result["candidate_written"] is False
    assert result["backup_created"] is False
    assert result["inventory_modified"] is False
    assert result["tests_executed"] is False
    assert result["global_validation_executed"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
print("ACEE6_C_TRANSACTION_PREPARATION_FINAL_LOCK_OK")
