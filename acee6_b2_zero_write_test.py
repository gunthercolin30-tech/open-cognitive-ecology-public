import hashlib
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

def snapshot(root):
    return {
        str(path.relative_to(root)): {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mode": path.stat().st_mode,
        }
        for path in root.rglob("*") if path.is_file()
    }

with TemporaryDirectory() as tmp:
    root = Path(tmp); (root / "ontology").mkdir()
    (root / "ontology_inventory.txt").write_text("sample\n", encoding="utf-8")
    decision = valid_acee5_decision(root)
    original = deepcopy(decision); before = snapshot(root)
    result = AceeInstallationExecutor(root=root, now_utc=fixed_now()).step(inputs=decision, persist=False)
    after = snapshot(root)
    assert before == after
    assert decision == original
    assert result["write_count"] == 0
    assert result["persistence_performed"] is False
    assert not (root / "ontology" / "sample_candidate.py.bak").exists()
print("ACEE6_B2_ZERO_WRITE_OK")
