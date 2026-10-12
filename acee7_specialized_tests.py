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
 root=Path(td); e=AceeValidationRunner(root=root); a=e.step(inputs=context(),persist=False); b=e.step(inputs=deepcopy(context()),persist=False); assert a["result_hash"]==b["result_hash"]
 x=e.step(inputs=context(),persist=True); c=context(); c["validation_id"]="validation-002"; c["timestamp_utc"]="2026-07-13T20:01:00Z"; y=e.step(inputs=c,persist=True); assert y["previous_validation_hash"]==x["result_hash"]
 records=[json.loads(z) for z in Path(y["history_path"]).read_text().splitlines() if z.strip()]; assert len(records)==2
 Path(y["history_path"]).write_text("{bad\n"); z=e.step(inputs=context(),persist=False); assert z["history_corrupted"] is True
print("ACEE7_SPECIALIZED_TESTS_OK")
