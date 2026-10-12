import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ("acee6_d3_functional_test.py","acee6_d3_failure_rollback_test.py","acee6_d3_no_execution_test.py","acee6_d3_idempotence_test.py","acee6_d3_final_lock.py"):
 r=subprocess.run([sys.executable,str(root/name)],cwd=str(root),timeout=90); assert r.returncode==0,name
print("ACEE6_D3_FAST_ACCEPTANCE_OK")
