import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for name in [
    "acee6_f2_second_crown_suite.py",
    "acee6_f2_fast_acceptance_suite.py",
    "acee6_f2_non_regression_test.py",
]:
    result = subprocess.run([sys.executable, str(ROOT / name)], cwd=str(ROOT), timeout=600)
    assert result.returncode == 0, name
print("ACEE6_F2_SECOND_CROWN_FINAL_LOCK_OK")
