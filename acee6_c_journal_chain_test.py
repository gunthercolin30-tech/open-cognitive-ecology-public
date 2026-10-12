import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=valid_acee5_decision(root), persist=True
    )
    records = [json.loads(line) for line in (Path(result["transaction_directory"]) / "journal.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [record["state"] for record in records] == ["PREPARING", "PREPARED"]
    previous = None
    for record in records:
        assert record["previous_record_hash"] == previous
        supplied = record["record_hash"]
        payload = {key: value for key, value in record.items() if key != "record_hash"}
        assert supplied == hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
        previous = supplied
print("ACEE6_C_JOURNAL_CHAIN_OK")
