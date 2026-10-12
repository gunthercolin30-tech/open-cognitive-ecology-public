from __future__ import annotations
import hashlib, py_compile, tempfile
from pathlib import Path
from ontology.acee_rollback_engine import AceeRollbackEngine

def context(root: Path):
    backup=root/"ontology"/"sample.py.bak"; backup.parent.mkdir(parents=True,exist_ok=True); backup.write_text("restored = True\n",encoding="utf-8")
    return {"rollback_request":{"transaction_id":"tx-001","reason":"validation_failure","targets":[{"destination":"ontology/sample.py","backup":"ontology/sample.py.bak","expected_backup_sha256":hashlib.sha256(backup.read_bytes()).hexdigest()}]},"governance_authorization":{"approved":True},"constitutional_authorization":{"approved":True},"dry_run":True,"execute":False,"timestamp_utc":"2026-07-13T18:00:00Z"}

def main():
    with tempfile.TemporaryDirectory() as td:
        py_compile.compile("ontology/acee_rollback_engine.py",cfile=str(Path(td)/"acee_rollback_engine.pyc"),doraise=True)
        root=Path(td)/"root"; r=AceeRollbackEngine(root=root).step(inputs=context(root),persist=False)
        assert r["rollback_status"]=="ACEE_ROLLBACK_ENGINE_READY" and r["rollback_ready"] is True
        assert r["rollback_performed"] is False and r["target_count"]==1
        assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
    print("ACEE11_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
