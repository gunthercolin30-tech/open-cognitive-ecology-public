#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path.home() / "open-cognitive-ecology"
TESTS = ["acee6_j1_final_report_functional_test.py", "acee6_j1_hash_tamper_degradation_test.py", "acee6_j1_persistence_test.py", "acee6_j1_public_contract_test.py", "acee6_j1_non_regression_test.py"]
for name in TESTS:
    completed = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)
print("ACEE6_J1_FAST_ACCEPTANCE_OK")
