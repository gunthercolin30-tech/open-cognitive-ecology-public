from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    decision = valid_acee5_decision(root)
    manifest = decision["installation_manifest"]
    inventory_targets = manifest["inventory_targets"]

    for relative in inventory_targets:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("unrelated_entry\n", encoding="utf-8")

    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=decision, persist=False)

    assert result["admissible"] is True
    assert result["normalized_plan"]["inventory_targets"] == sorted(
        inventory_targets
    )

    impacts = result["dry_run_plan"]["inventory_impacts"]
    assert len(impacts) == len(inventory_targets)
    assert all(item["exists_before"] is True for item in impacts)
    assert all(item["operation"] == "update" for item in impacts)
    assert [item["path"] for item in impacts] == sorted(inventory_targets)
    assert (
        result["dry_run_plan"]["summary"]["inventories_impacted"]
        == len(impacts)
    )

    assert result["read_only"] is True
    assert result["write_count"] == 0
    assert result["inventory_modified"] is False
    assert result["persistence_performed"] is False

    for relative in inventory_targets:
        path = root / relative
        assert path.read_text(encoding="utf-8") == "unrelated_entry\n"

print("ACEE6_B2_INVENTORY_PROJECTION_OK")
