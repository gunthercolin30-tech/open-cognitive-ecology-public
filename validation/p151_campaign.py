from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for n in ["p151_functional_test.py","p151_degradation_test.py","p151_adversarial_test.py","p151_non_regression_test.py","p151_adversarial_crown_test.py","p151_cwd_independence_test.py","p151_evidence_report.py","p151_final_lock.py","p151_final_lock_integrity_check.py","p151_final_lock_tamper_test.py"]:
 r=subprocess.run([sys.executable,str(ROOT/"validation"/n)],cwd=str(ROOT)); assert r.returncode==0,n
print("P151_CAMPAIGN_OK")
