from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    value = payload(root)
    first = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=value, persist=True)
    second = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=value, persist=True)
    assert first["transaction_state"] == "LOCALLY_VALIDATED", first
    assert second["transaction_state"] == "LOCALLY_VALIDATED", second
    assert second["local_validation_replayed"] is True
    assert second["persistence_performed"] is False
    assert first["local_validation_report_hash"] == second["local_validation_report_hash"]
print("ACEE6_F1_RESTART_REPLAY_OK")
