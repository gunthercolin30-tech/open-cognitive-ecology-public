from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for n in ("p004_functional_test.py","p004_degradation_test.py","p004_adversarial_test.py","p004_non_regression_test.py","p004_cwd_test.py","p004_adversarial_crown_test.py","p004_final_lock.py","p004_final_lock_integrity_check.py","p004_final_lock_tamper_test.py"):
 subprocess.run([sys.executable,str(ROOT/"validation"/n)],cwd=ROOT,check=True)
print("P004_CAMPAIGN_OK")
