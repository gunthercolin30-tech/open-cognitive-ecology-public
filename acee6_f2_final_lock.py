import subprocess, sys
for name in ["acee6_f2_fast_acceptance_suite.py", "acee6_f2_non_regression_test.py"]:
    result = subprocess.run([sys.executable, name], timeout=900)
    assert result.returncode == 0, name
print("ACEE6_F2_GLOBAL_VALIDATION_FINAL_LOCK_OK")
