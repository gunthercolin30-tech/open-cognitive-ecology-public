from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    decision["installation_manifest"]["manifest_hash"] = "0" * 64
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=decision, persist=False)
    assert result["admissible"] is False
    assert result["dry_run_plan"] is None
    assert result["write_count"] == 0
    assert "manifest_hash_mismatch" in result["blocking_reasons"]
print("ACEE6_B2_DEGRADATION_OK")
