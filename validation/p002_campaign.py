
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for n in ["p002_minimal_sufficiency_functional_test.py","p002_minimal_sufficiency_degradation_test.py","p002_minimal_sufficiency_adversarial_test.py","p002_minimal_sufficiency_non_regression_test.py","p002_final_lock.py"]:
    subprocess.run([sys.executable,str(ROOT/"validation"/n)],cwd=ROOT,check=True)
print("P002_CAMPAIGN_OK")
