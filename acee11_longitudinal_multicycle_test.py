from __future__ import annotations
import json, tempfile
from copy import deepcopy
from pathlib import Path
from acee11_fast_acceptance_suite import context
from ontology.acee_rollback_engine import AceeRollbackEngine
with tempfile.TemporaryDirectory() as td:
    root=Path(td)/"root"; base=context(root); engine=AceeRollbackEngine(root=root); previous=None
    for i in range(12):
        c=deepcopy(base); c["rollback_request"]["transaction_id"]=f"cycle-{i}"; c["timestamp_utc"]=f"2026-07-13T19:{i:02d}:00Z"; r=engine.step(inputs=c,persist=True)
        assert r["previous_record_hash"]==previous; previous=r["record_hash"]
    records=[json.loads(x) for x in Path(r["history_path"]).read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(records)==12
print("ACEE11_LONGITUDINAL_MULTICYCLE_OK")
