import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import ontology.acee_installation_executor as module
from acee6_b1_test_support import fixed_now, valid_acee5_decision

assert tuple(inspect.signature(module.AceeInstallationExecutor.step).parameters) == ("self", "inputs", "persist")
for name in ("STATUS_ADMISSIBLE", "STATUS_REJECTED", "REQUIRED_MANIFEST_FIELDS", "REQUIRED_INVENTORY_TARGETS", "ACCEPTED_ACEE5_SCHEMAS"):
    assert hasattr(module, name)
with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    result = module.AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=valid_acee5_decision(root), persist=False)
    assert result["status"] == module.STATUS_ADMISSIBLE
    assert result["normalized_plan"]["target_path"] == "ontology/sample_candidate.py"
    assert result["read_only"] is True
print("ACEE6_B2_NON_REGRESSION_OK")
