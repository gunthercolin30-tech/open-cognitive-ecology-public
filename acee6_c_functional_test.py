import json
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
    assert result["status"] == "ACEE6_TRANSACTION_PREPARED"
    assert result["transaction_state"] == "PREPARED"
    assert result["transaction_prepared"] is True
    assert result["journal_persisted"] is True
    assert result["journal_fsynced"] is True
    assert result["directory_fsynced"] is True
    assert result["lock_acquired"] is True
    assert result["snapshot_hashes_recorded"] is True
    assert result["candidate_written"] is False
    assert result["inventory_modified"] is False
    transaction_dir = Path(result["transaction_directory"])
    assert (transaction_dir / "journal.jsonl").is_file()
    assert (transaction_dir / "latest_state.json").is_file()
    assert (transaction_dir / "snapshot.json").is_file()
    latest = json.loads((transaction_dir / "latest_state.json").read_text(encoding="utf-8"))
    assert latest["transaction_state"] == "PREPARED"
print("ACEE6_C_FUNCTIONAL_OK")
