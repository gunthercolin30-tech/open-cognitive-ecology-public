import subprocess,sys
for n in ["acee6_f1_fast_acceptance_suite.py","acee6_f1_non_regression_test.py"]:
 r=subprocess.run([sys.executable,n],timeout=300);assert r.returncode==0,n
print("ACEE6_F1_LOCAL_VALIDATION_FINAL_LOCK_OK")
