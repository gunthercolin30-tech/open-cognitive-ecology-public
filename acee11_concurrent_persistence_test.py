from __future__ import annotations
import json, tempfile
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from acee11_fast_acceptance_suite import context
from ontology.acee_rollback_engine import AceeRollbackEngine
with tempfile.TemporaryDirectory() as td:
    root=Path(td)/"root"; base=context(root)
    def run(i):
        c=deepcopy(base); c["rollback_request"]["transaction_id"]=f"tx-{i}"; c["timestamp_utc"]=f"2026-07-13T18:{i:02d}:00Z"; return AceeRollbackEngine(root=root).step(inputs=c,persist=True)
    with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,range(8)))
    history=Path(results[0]["history_path"]); records=[json.loads(x) for x in history.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(records)==8 and len({x["transaction_id"] for x in records})==8
print("ACEE11_CONCURRENT_PERSISTENCE_OK")
