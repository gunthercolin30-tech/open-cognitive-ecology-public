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
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    first = executor.step(inputs=decision, persist=True)
    assert first["transaction_state"] == "PREPARED"

    target.write_text("changed_after_prepare\n", encoding="utf-8")
    second = executor.step(inputs=decision, persist=True)

    assert second["transaction_prepared"] is False
    assert second["transaction_state"] == "STATE_CORRUPTED"
    assert second["status"] == "ACEE6_TRANSACTION_PREPARATION_REJECTED"
    assert "existing_transaction_snapshot_divergence" in (
        second["blocking_reasons"]
    )
    assert second["candidate_written"] is False

print("ACEE6_C_SNAPSHOT_DIVERGENCE_OK")
