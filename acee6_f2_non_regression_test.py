import subprocess, sys
for name in ["acee6_f1_fast_acceptance_suite.py", "acee6_f1_second_crown_suite.py", "acee6_e_fast_acceptance_suite.py"]:
    result = subprocess.run([sys.executable, name], timeout=600)
    assert result.returncode == 0, name
print("ACEE6_F2_NON_REGRESSION_OK")
