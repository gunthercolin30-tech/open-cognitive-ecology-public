import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload, seed
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)
    target = root / "ontology" / "sample_candidate.py"
    original = "VALUE = 1\n"
    target.write_text(original, encoding="utf-8")
    original_hash = hashlib.sha256(target.read_bytes()).hexdigest()
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=payload(root, failing_role="functional"), persist=True
    )
    assert result["transaction_state"] == "ROLLED_BACK", result
    assert result["rollback_executed"] is True
    assert result["target_rollback_succeeded"] is True
    assert target.read_text(encoding="utf-8") == original
    assert hashlib.sha256(target.read_bytes()).hexdigest() == original_hash
print("ACEE6_F1_PREEXISTING_CANDIDATE_ROLLBACK_OK")
