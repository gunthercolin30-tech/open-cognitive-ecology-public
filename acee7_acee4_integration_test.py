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
r=AceeValidationRunner(root=Path("/nonexistent")).step(inputs=context(),persist=False)
phase={"status":"completed" if r["validation_passed"] else "failed","passed":r["validation_passed"],"score":1.0 if r["validation_passed"] else 0.0}
assert phase["passed"] is True and r["rollback_required"] is False
print("ACEE7_ACEE4_INTEGRATION_OK")
