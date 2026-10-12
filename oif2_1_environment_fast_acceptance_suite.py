from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
PYTHON = ROOT / ".venv-oif" / "bin" / "python"

TESTS = (
    "oif2_1_environment_functional_test.py",
    "oif2_1_environment_degradation_test.py",
    "oif2_1_environment_non_regression_test.py",
    "oif2_1_environment_incompatible_python_test.py",
    "oif2_1_environment_recreation_test.py",
    "oif2_1_environment_idempotent_install_test.py",
    "oif2_1_environment_homebrew_path_drift_test.py",
    "oif2_1_environment_corrupted_lock_test.py",
)

assert PYTHON.is_file(), PYTHON

for name in TESTS:
    test = ROOT / name
    assert test.is_file(), test
    completed = subprocess.run(
        [str(PYTHON), str(test)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=1800,
        check=False,
    )
    print(completed.stdout, end="")
    if completed.returncode:
        print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)

print("OIF2_1_FAST_ACCEPTANCE_ALL_OK")
