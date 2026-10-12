from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    real = root / "real"
    real.mkdir()
    target = real / "sample_candidate.py"
    target.write_text("before\n", encoding="utf-8")
    (root / "ontology").symlink_to(real, target_is_directory=True)

    decision = valid_acee5_decision(root)
    inputs = {
        "acee5_decision": decision,
        "admission_context": {"requested_stage": "ACEE6-D1"},
    }

    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(inputs=inputs, persist=True)

    assert result["admissible"] is False
    assert result["status"] == "ACEE6_INSTALLATION_PLAN_REJECTED"
    assert result["write_count"] == 0
    assert result["persistence_performed"] is False
    assert result["candidate_written"] is False
    assert result["backup_created"] is False
    assert result["inventory_modified"] is False
    assert result["blocking_reasons"]
    assert target.read_text(encoding="utf-8") == "before\n"
    assert not (real / "sample_candidate.py.bak").exists()

print("ACEE6_D1_PARENT_SYMLINK_OK")
