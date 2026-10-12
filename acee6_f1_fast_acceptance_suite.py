import subprocess,sys
for n in ["acee6_f1_functional_test.py","acee6_f1_order_contract_test.py","acee6_f1_failure_rollback_test.py","acee6_f1_idempotence_test.py","acee6_f1_report_tamper_test.py"]:
 r=subprocess.run([sys.executable,n],timeout=180);assert r.returncode==0,n
print("ACEE6_F1_FAST_ACCEPTANCE_OK")
