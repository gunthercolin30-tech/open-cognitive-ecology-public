import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ("acee6_d1_fast_acceptance_suite.py","acee6_d2_fast_acceptance_suite.py"):
 r=subprocess.run([sys.executable,str(root/name)],cwd=str(root),timeout=180); assert r.returncode==0,name
print("ACEE6_D3_NON_REGRESSION_OK")
