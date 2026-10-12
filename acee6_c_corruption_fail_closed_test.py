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
    (Path(first["transaction_directory"]) / "latest_state.json").write_text("{corrupted", encoding="utf-8")
    second = executor.step(inputs=decision, persist=True)
    assert second["transaction_prepared"] is False
    assert second["transaction_state"] == "STATE_CORRUPTED"
    assert "existing_transaction_state_corrupted" in second["blocking_reasons"]
print("ACEE6_C_CORRUPTION_FAIL_CLOSED_OK")
