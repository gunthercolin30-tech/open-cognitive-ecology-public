from pathlib import Path
import subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
for n in ("p003_functional_test.py","p003_degradation_test.py","p003_adversarial_test.py","p003_non_regression_test.py"):
 with tempfile.TemporaryDirectory() as td: subprocess.run([sys.executable,str(ROOT/"validation"/n)],cwd=td,check=True,stdout=subprocess.DEVNULL)
print("P003_CWD_INDEPENDENCE_OK")
