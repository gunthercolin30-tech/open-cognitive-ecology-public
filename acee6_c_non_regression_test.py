from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=valid_acee5_decision(root), persist=False
    )
    assert result["status"] == "ACEE6_INSTALLATION_PLAN_ADMISSIBLE"
    assert result["dry_run_status"] == "ACEE6_INSTALLATION_DRY_RUN_READY"
    assert result["write_count"] == 0
    assert result["persistence_performed"] is False
    assert "transaction_id" not in result
print("ACEE6_C_NON_REGRESSION_OK")
