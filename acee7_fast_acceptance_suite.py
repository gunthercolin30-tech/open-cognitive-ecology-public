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
import tempfile, py_compile
from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner

def main():
    with tempfile.TemporaryDirectory() as td: py_compile.compile("ontology/acee_validation_runner.py",cfile=str(Path(td)/"x.pyc"),doraise=True)
    r=AceeValidationRunner(root=Path("/nonexistent")).step(inputs=context(),persist=False)
    assert r["validation_status"]=="ACEE_VALIDATION_COMPLETE" and r["validation_passed"] is True and r["error_count"]==0
    assert r["shell_used"] is False and r["functional_conclusion_only"] is True
    print("ACEE7_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
