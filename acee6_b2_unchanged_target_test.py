import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    target = root / "ontology" / "sample_candidate.py"
    candidate_bytes = b"candidate-content\n"
    target.write_bytes(candidate_bytes)

    candidate_hash = hashlib.sha256(candidate_bytes).hexdigest()
    from acee5_hardening_test_support import valid_context
    from ontology.acee_governed_code_generation_gate import (
        AceeGovernedCodeGenerationGate,
    )
    decision = AceeGovernedCodeGenerationGate(root=root).step(
        inputs=valid_context(root, candidate_hash=candidate_hash),
        persist=False,
    )

    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=decision, persist=False)

    assert result["admissible"] is True
    change = result["dry_run_plan"]["candidate_change"]
    assert change["operation"] == "unchanged"
    assert result["dry_run_plan"]["files_to_create"] == []
    assert result["dry_run_plan"]["files_to_modify"] == []
    assert result["dry_run_plan"]["unchanged_files"] == [
        "ontology/sample_candidate.py"
    ]
    assert result["dry_run_plan"]["rollback_plan"]["required"] in (True, False)
    assert result["write_count"] == 0

print("ACEE6_B2_UNCHANGED_TARGET_OK")
