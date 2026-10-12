import hashlib
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor

def snapshot(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }

with TemporaryDirectory() as tmp:
    root=Path(tmp); (root/"ontology").mkdir()
    decision=valid_acee5_decision(root)
    before=snapshot(root); original=deepcopy(decision)
    result=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(decision,persist=False)
    after=snapshot(root)
    assert before==after
    assert decision==original
    assert result["persistence_performed"] is False
print("ACEE6_B1_NON_REGRESSION_OK")
