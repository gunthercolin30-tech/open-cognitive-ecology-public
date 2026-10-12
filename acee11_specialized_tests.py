from __future__ import annotations
import hashlib, json, tempfile
from copy import deepcopy
from pathlib import Path
from acee11_fast_acceptance_suite import context
from ontology.acee_rollback_engine import AceeRollbackEngine

def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)/"root"; c=context(root); e=AceeRollbackEngine(root=root)
        a=e.step(inputs=c,persist=False); b=e.step(inputs=deepcopy(c),persist=False); assert a["result_hash"]==b["result_hash"]
        bad=deepcopy(c); bad["rollback_request"]["targets"][0]["expected_backup_sha256"]="0"*64; r=e.step(inputs=bad,persist=False); assert any("backup_hash_mismatch" in x for x in r["blocking_reasons"])
        outside=deepcopy(c); outside["rollback_request"]["targets"][0]["destination"]="/tmp/escape.py"; r=e.step(inputs=outside,persist=False); assert "target_0_outside_root" in r["blocking_reasons"]
        rejected=deepcopy(c); rejected["governance_authorization"]={"approved":False}; r=e.step(inputs=rejected,persist=False); assert r["rollback_status"]=="ACEE_ROLLBACK_BLOCKED"
        x=e.step(inputs=c,persist=True); c2=deepcopy(c); c2["timestamp_utc"]="2026-07-13T18:01:00Z"; y=e.step(inputs=c2,persist=True); assert y["previous_record_hash"]==x["record_hash"]
        records=[json.loads(line) for line in Path(y["history_path"]).read_text(encoding="utf-8").splitlines() if line.strip()]; assert len(records)==2
    print("ACEE11_SPECIALIZED_TESTS_OK")
if __name__=="__main__": main()
