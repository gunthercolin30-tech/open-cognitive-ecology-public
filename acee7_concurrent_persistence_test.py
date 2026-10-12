from __future__ import annotations

def context():
    return {
        "validation_id": "validation-001",
        "timestamp_utc": "2026-07-13T20:00:00Z",
        "scope": "acee4",
        "mode": "targeted",
        "command_results": [
            {"name": "compile", "returncode": 0, "stdout": "COMPILE_OK", "stderr": "", "duration_seconds": 0.01},
            {"name": "fast_acceptance", "returncode": 0, "stdout": "ACEE4_FAST_ACCEPTANCE_OK", "stderr": "", "duration_seconds": 0.02},
            {"name": "final_lock", "returncode": 0, "stdout": "ACEE_AUTONOMOUS_CYCLE_MANAGER_FINAL_LOCK_OK", "stderr": "", "duration_seconds": 0.03},
        ],
    }
from concurrent.futures import ThreadPoolExecutor
import json, tempfile
from copy import deepcopy
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner
with tempfile.TemporaryDirectory() as td:
 root=Path(td)
 def run(i):
  c=deepcopy(context()); c["validation_id"]=f"validation-{i}"; c["timestamp_utc"]=f"2026-07-13T21:{i:02d}:00Z"; return AceeValidationRunner(root=root).step(inputs=c,persist=True)
 with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,range(8)))
 records=[json.loads(x) for x in Path(results[0]["history_path"]).read_text().splitlines() if x.strip()]
 assert len(records)==8
 for i in range(1,len(records)): assert records[i]["previous_validation_hash"]==records[i-1]["result_hash"]
print("ACEE7_CONCURRENT_PERSISTENCE_OK")
