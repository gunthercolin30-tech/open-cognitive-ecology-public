import subprocess, sys
for name in ["acee6_f2_functional_test.py", "acee6_f2_failure_rollback_test.py", "acee6_f2_idempotence_test.py", "acee6_f2_report_tamper_test.py"]:
    result = subprocess.run([sys.executable, name], timeout=300)
    assert result.returncode == 0, name
print("ACEE6_F2_FAST_ACCEPTANCE_OK")
