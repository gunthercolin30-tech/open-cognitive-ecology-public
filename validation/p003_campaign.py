from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for n in ("p003_functional_test.py","p003_degradation_test.py","p003_adversarial_test.py","p003_non_regression_test.py","p003_cwd_test.py","p003_final_lock.py","p003_final_lock_integrity_check.py","p003_final_lock_tamper_test.py"): subprocess.run([sys.executable,str(ROOT/"validation"/n)],cwd=ROOT,check=True)
print("P003_CAMPAIGN_OK")
