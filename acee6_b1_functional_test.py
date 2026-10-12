from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    original = deepcopy(decision)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    first = executor.step(decision)
    second = executor.step(decision)
    assert decision == original
    assert first["result_hash"] == second["result_hash"]
    assert first["normalized_plan"]["target_path"] == "ontology/sample_candidate.py"
    assert first["normalized_plan"]["manifest_hash"] == decision["installation_manifest"]["manifest_hash"]
print("ACEE6_B1_FUNCTIONAL_OK")
