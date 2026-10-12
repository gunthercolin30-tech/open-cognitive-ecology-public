import subprocess,sys
for f in ["acee6_k3_functional_test.py","acee6_k3_degradation_test.py","acee6_k3_non_regression_test.py","acee6_k3_report_tamper_test.py"]: subprocess.run([sys.executable,f],check=True,timeout=120)
print("ACEE6_K3_FAST_ACCEPTANCE_OK")
