import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

def sha_bytes(data): return hashlib.sha256(data).hexdigest()

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    target = root / "ontology" / "sample_candidate.py"
    target.write_bytes(b"old-content\n")
    decision = valid_acee5_decision(root)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=decision, persist=False)
    change = result["dry_run_plan"]["candidate_change"]
    assert change["operation"] == "modify"
    assert change["before_sha256"] == sha_bytes(b"old-content\n")
    assert change["after_sha256"] == "a" * 64
print("ACEE6_B2_EXISTING_TARGET_OK")
