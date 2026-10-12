from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    first = executor.step(inputs=decision, persist=False); second = executor.step(inputs=decision, persist=False)
    assert first == second
    assert first["dry_run_plan"]["plan_hash"] == second["dry_run_plan"]["plan_hash"]
print("ACEE6_B2_DETERMINISM_OK")
