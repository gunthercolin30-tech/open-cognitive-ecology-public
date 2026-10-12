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
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner
c=context(); c["command_results"]=[{"name":"warn","returncode":0,"stderr":"RuntimeWarning: benign\nNotOpenSSLWarning: benign"}]
r=AceeValidationRunner(root=Path("/nonexistent")).step(inputs=c,persist=False)
assert r["validation_passed"] is True and r["warning_count"]==2 and len(r["benign_warnings"])==2
print("ACEE7_BENIGN_WARNING_OK")
