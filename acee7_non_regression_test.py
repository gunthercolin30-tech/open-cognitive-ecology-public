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
import hashlib
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner
paths=[Path("ontology/acee_autonomous_cycle_manager.py"),Path("ontology/acee_rollback_engine.py"),Path("validation/main.py"),Path("dependency_registry.py")]
def d(p): return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
b={str(p):d(p) for p in paths}; r=AceeValidationRunner().step(inputs=context(),persist=False); a={str(p):d(p) for p in paths}
assert b==a and r["persisted"] is False and r["global_validation_executed"] is False
print("ACEE7_NON_REGRESSION_OK")
