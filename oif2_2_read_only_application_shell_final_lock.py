from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif/bin/python"
SUITE = ROOT / "oif2_2_fast_acceptance_suite.py"
REPORT = ROOT / "oif2_2_read_only_application_shell_final_lock_report.json"

FILES = (
    ROOT / "oif/application/shell_service.py",
    ROOT / "oif/ui/operational_shell.py",
    ROOT / "oif2_2_read_only_shell_functional_test.py",
    ROOT / "oif2_2_read_only_shell_degradation_test.py",
    ROOT / "oif2_2_read_only_shell_non_regression_test.py",
    SUITE,
)

completed = subprocess.run(
    [str(PYTHON), str(SUITE)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=1200,
    check=False,
)
assert completed.returncode == 0, completed.stdout + completed.stderr

hashes = {
    str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in FILES
}
report = {
    "milestone": "OIF2-2",
    "primitive": "oif2_read_only_application_shell",
    "status": "locked",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "read_only_shell_validated": True,
    "renderer_replaceability_validated": True,
    "renderer_direct_write_absent": True,
    "renderer_shell_execution_absent": True,
    "provider_degradation_validated": True,
    "legacy_review_interface_preserved": True,
    "hashes": hashes,
    "functional_conclusion_only": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
}
REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(completed.stdout, end="")
print("OIF2_2_READ_ONLY_APPLICATION_SHELL_FINAL_LOCK_OK")
