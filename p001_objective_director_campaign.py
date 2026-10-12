import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
steps = [
    "p001_objective_director_functional_test.py",
    "p001_objective_director_degradation_test.py",
    "p001_objective_director_non_regression_test.py",
    "p001_objective_director_cwd_test.py",
    "p001_objective_director_final_lock.py",
]
for step in steps:
    proc = subprocess.run([sys.executable, str(ROOT / step)], cwd=str(ROOT))
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
print("P001_CAMPAIGN_OK")
