from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    first_decision = valid_acee5_decision(root)
    first = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=first_decision, persist=False)

    from acee5_hardening_test_support import valid_context
    from ontology.acee_governed_code_generation_gate import (
        AceeGovernedCodeGenerationGate,
    )
    second_decision = AceeGovernedCodeGenerationGate(root=root).step(
        inputs=valid_context(root, candidate_hash="b" * 64),
        persist=False,
    )

    second = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=second_decision, persist=False)

    assert first["admissible"] is True
    assert second["admissible"] is True
    assert (
        first["dry_run_plan"]["plan_hash"]
        != second["dry_run_plan"]["plan_hash"]
    )

print("ACEE6_B2_PLAN_HASH_SENSITIVITY_OK")
