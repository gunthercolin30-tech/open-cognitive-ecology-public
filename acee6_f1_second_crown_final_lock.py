import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITES = [
    "acee6_f1_second_crown_suite.py",
    "acee6_f1_fast_acceptance_suite.py",
    "acee6_f1_non_regression_test.py",
]
for name in SUITES:
    result = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), timeout=600)
    assert result.returncode == 0, name
print("ACEE6_F1_SECOND_CROWN_FINAL_LOCK_OK")
