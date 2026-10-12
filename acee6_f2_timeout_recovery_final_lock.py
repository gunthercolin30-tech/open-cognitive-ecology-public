import subprocess
import sys

for name in [
    "acee6_f2_timeout_recovery_suite.py",
    "acee6_f2_second_crown_suite.py",
    "acee6_f2_fast_acceptance_suite.py",
]:
    result = subprocess.run([sys.executable, name], timeout=600)
    assert result.returncode == 0, name
print("ACEE6_F2_TIMEOUT_RECOVERY_FINAL_LOCK_OK")
