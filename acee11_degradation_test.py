import tempfile
from pathlib import Path
from ontology.acee_rollback_engine import AceeRollbackEngine
with tempfile.TemporaryDirectory() as td:
    r=AceeRollbackEngine(root=Path(td)).step(inputs={},persist=False)
    assert r["rollback_status"]=="ACEE_ROLLBACK_BLOCKED"
    assert r["rollback_performed"] is False
    assert "targets_missing" in r["blocking_reasons"]
    assert "governance_authorization_missing_or_rejected" in r["blocking_reasons"]
print("ACEE11_DEGRADATION_OK")
