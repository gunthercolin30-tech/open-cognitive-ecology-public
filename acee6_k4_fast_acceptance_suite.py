from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TESTS = [
 "acee6_k4_functional_test.py",
 "acee6_k4_degradation_test.py",
 "acee6_k4_non_regression_test.py",
 "acee6_k4_report_tamper_test.py",
 "acee6_k4_cleanup_test.py",
]
for name in TESTS:
    subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), check=True, timeout=120)
print("ACEE6_K4_FAST_ACCEPTANCE_OK")
