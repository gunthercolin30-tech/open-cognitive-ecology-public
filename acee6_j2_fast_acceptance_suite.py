from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS = [
    "acee6_j2_functional_test.py",
    "acee6_j2_degradation_test.py",
    "acee6_j2_non_regression_test.py",
    "acee6_j2_unknown_state_test.py",
]
for name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), text=True, capture_output=True, timeout=60)
    if completed.returncode != 0:
        raise SystemExit(f"{name} failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
print("ACEE6_J2_FAST_ACCEPTANCE_OK")
