import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


class InterruptAfterPreparing(AceeInstallationExecutor):
    def __post_init__(self):
        super().__post_init__()
        self._journal_calls = 0

    def _append_journal_record(self, journal, payload, previous_hash):
        self._journal_calls += 1
        result = super()._append_journal_record(
            journal,
            payload,
            previous_hash,
        )
        if self._journal_calls == 1:
            raise RuntimeError("simulated_interruption_after_preparing")
        return result


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)

    try:
        InterruptAfterPreparing(
            root=root,
            now_utc=fixed_now(),
        ).step(inputs=decision, persist=True)
    except RuntimeError as exc:
        assert str(exc) == "simulated_interruption_after_preparing"
    else:
        raise AssertionError("interruption_not_triggered")

    journals = list((root / "acee6_transactions").glob("*/journal.jsonl"))
    assert len(journals) == 1
    initial_records = [
        json.loads(line)
        for line in journals[0].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [item["state"] for item in initial_records] == ["PREPARING"]

    recovered = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=decision, persist=True)

    assert recovered["status"] == "ACEE6_TRANSACTION_PREPARED"
    assert recovered["transaction_state"] == "PREPARED"
    assert recovered["candidate_written"] is False

    latest = Path(recovered["latest_state_path"])
    payload = json.loads(latest.read_text(encoding="utf-8"))
    assert payload["transaction_state"] == "PREPARED"

print("ACEE6_C_PREPARING_INTERRUPTION_RECOVERY_OK")
