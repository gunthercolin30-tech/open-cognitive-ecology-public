from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=valid_acee5_decision(root)
    tampered=deepcopy(decision)
    tampered["installation_manifest"]["target_path"]="ontology/other.py"
    result=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(tampered)
    assert result["admissible"] is False
    assert "manifest_hash_mismatch" in result["blocking_reasons"]
print("ACEE6_B1_MANIFEST_TAMPER_OK")
