from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    decision = valid_acee5_decision(root)
    original = deepcopy(decision)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=decision, persist=False)
    assert decision == original
    assert result["admissible"] is True
    assert result["dry_run"] is True
    assert result["write_count"] == 0
    plan = result["dry_run_plan"]
    assert plan["candidate_change"]["operation"] == "create"
    assert plan["candidate_change"]["target_path"] == "ontology/sample_candidate.py"
    assert plan["summary"]["files_created"] == 1
    assert plan["summary"]["files_modified"] == 0
    assert plan["rollback_plan"]["required"] is True
    assert plan["rollback_plan"]["executor"] == "acee_rollback_engine"
print("ACEE6_B2_FUNCTIONAL_OK")
