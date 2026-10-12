from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=decision, persist=False)
    assert result["status"] == "ACEE6_INSTALLATION_PLAN_ADMISSIBLE"
    assert result["admissible"] is True
    assert result["read_only"] is True
    assert all(result[key] is False for key in (
        "backup_created", "candidate_written", "candidate_compiled",
        "tests_executed", "global_validation_executed",
        "rollback_executed", "inventory_modified", "persistence_performed",
    ))
print("ACEE6_B1_FAST_ACCEPTANCE_OK")
