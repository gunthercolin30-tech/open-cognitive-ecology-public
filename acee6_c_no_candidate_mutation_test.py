import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()
    target = root / "ontology" / "sample_candidate.py"
    target.write_text("original\n", encoding="utf-8")
    before = hashlib.sha256(target.read_bytes()).hexdigest()
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(
        inputs=valid_acee5_decision(root), persist=True
    )
    assert hashlib.sha256(target.read_bytes()).hexdigest() == before
    assert result["candidate_written"] is False
    assert result["backup_created"] is False
    assert result["candidate_compiled"] is False
    assert result["tests_executed"] is False
    assert result["global_validation_executed"] is False
print("ACEE6_C_NO_CANDIDATE_MUTATION_OK")
