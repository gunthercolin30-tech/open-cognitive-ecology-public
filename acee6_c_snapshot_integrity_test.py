import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    target = root / "ontology" / "sample_candidate.py"
    target.write_text("before\n", encoding="utf-8")
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=valid_acee5_decision(root), persist=True
    )
    snapshot = json.loads((Path(result["transaction_directory"]) / "snapshot.json").read_text(encoding="utf-8"))
    entry = next(item for item in snapshot["entries"] if item["relative_path"] == "ontology/sample_candidate.py")
    assert entry["sha256"] == hashlib.sha256(b"before\n").hexdigest()
    assert snapshot["snapshot_hash"] == result["snapshot_hash"]
print("ACEE6_C_SNAPSHOT_INTEGRITY_OK")
