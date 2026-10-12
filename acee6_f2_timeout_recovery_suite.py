import subprocess
import sys

for name in [
    "full_validation_timeout_retry_test.py",
    "full_validation_persistent_timeout_test.py",
    "full_validation_timeout_retry_bound_test.py",
]:
    result = subprocess.run([sys.executable, name], timeout=120)
    assert result.returncode == 0, name
print("ACEE6_F2_TIMEOUT_RECOVERY_SUITE_OK")
