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
import json, tempfile
from copy import deepcopy
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner
with tempfile.TemporaryDirectory() as td:
 e=AceeValidationRunner(root=Path(td)); prev=None
 for i in range(12):
  c=deepcopy(context()); c["validation_id"]=f"long-{i}"; c["timestamp_utc"]=f"2026-07-13T22:{i:02d}:00Z"; r=e.step(inputs=c,persist=True); assert r["previous_validation_hash"]==prev; prev=r["result_hash"]
 records=[json.loads(x) for x in Path(r["history_path"]).read_text().splitlines() if x.strip()]; assert len(records)==12
print("ACEE7_LONGITUDINAL_MULTICYCLE_OK")
