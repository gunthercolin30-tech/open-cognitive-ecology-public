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
    journal = Path(first["journal_path"])
    with journal.open("ab") as stream:
        stream.write(b'{"state":"PREPARED"')
        stream.flush()

    second = executor.step(inputs=decision, persist=True)

    assert second["transaction_prepared"] is False
    assert second["transaction_state"] == "STATE_CORRUPTED"
    assert second["status"] == "ACEE6_TRANSACTION_PREPARATION_REJECTED"
    assert any(
        reason in second["blocking_reasons"]
        for reason in (
            "existing_transaction_journal_corrupted",
            "existing_transaction_state_corrupted",
        )
    )
    assert second["candidate_written"] is False

print("ACEE6_C_PARTIAL_JOURNAL_FAIL_CLOSED_OK")
