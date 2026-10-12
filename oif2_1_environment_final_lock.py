from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif" / "bin" / "python"
SUITE = ROOT / "oif2_1_environment_fast_acceptance_suite.py"
LOCK = ROOT / "requirements" / "oif-nicegui.lock.txt"
INTERPRETER = ROOT / "requirements" / "oif-python-interpreter.txt"
REPORT = ROOT / "oif2_1_environment_final_lock_report.json"

completed = subprocess.run(
    [str(PYTHON), str(SUITE)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=5400,
    check=False,
)
assert completed.returncode == 0, completed.stdout + completed.stderr
assert LOCK.is_file() and LOCK.stat().st_size > 0, LOCK
assert INTERPRETER.is_file() and INTERPRETER.stat().st_size > 0, INTERPRETER

report = {
    "milestone": "OIF2-1C",
    "status": "locked",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "lock_sha256": hashlib.sha256(LOCK.read_bytes()).hexdigest(),
    "interpreter_record": INTERPRETER.read_text(encoding="utf-8").strip(),
    "full_recreation_validated": True,
    "idempotent_install_validated": True,
    "incompatible_python_rollback_validated": True,
    "homebrew_path_drift_validated": True,
    "corrupted_lock_fail_closed_validated": True,
    "partial_environment_rollback_validated": True,
    "functional_conclusion_only": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
}
REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print(completed.stdout, end="")
print("OIF2_1_ENVIRONMENT_FINAL_LOCK_OK")
