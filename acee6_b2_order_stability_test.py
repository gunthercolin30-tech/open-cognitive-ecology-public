from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    decision = valid_acee5_decision(root)
    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=decision, persist=False)

    assert result["admissible"] is True
    tests = result["dry_run_plan"]["tests_to_execute"]
    assert [item["execution_order"] for item in tests] == list(
        range(len(tests))
    )
    assert [item["path"] for item in tests] == list(
        result["normalized_plan"]["test_paths"]
    )
    assert [item["path"] for item in result["dry_run_plan"]["inventory_impacts"]] == list(
        result["normalized_plan"]["inventory_targets"]
    )

print("ACEE6_B2_ORDER_STABILITY_OK")
