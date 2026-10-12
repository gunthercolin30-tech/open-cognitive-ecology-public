from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    first = executor.step(inputs=decision, persist=True)
    second = executor.step(inputs=decision, persist=True)
    assert first["transaction_id"] == second["transaction_id"]
    assert second["transaction_state"] == "PREPARED"
    assert second["preparation_replayed"] is True
    assert first["snapshot_hash"] == second["snapshot_hash"]
print("ACEE6_C_IDEMPOTENCE_OK")
