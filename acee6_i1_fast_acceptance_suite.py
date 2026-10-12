#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = ["acee6_i1_functional_test.py", "acee6_i1_degradation_test.py", "acee6_i1_non_regression_test.py"]
for test in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT / test)], cwd=str(ROOT), check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)
print("ACEE6_I1_FAST_ACCEPTANCE_OK")
