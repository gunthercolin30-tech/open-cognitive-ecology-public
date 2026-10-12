from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TESTS=('acee6_k6_checkpoint_test.py','acee6_k6_before_checkpoint_recovery_test.py','acee6_k6_checkpoint_tamper_test.py','acee6_k6_chain_tamper_test.py','acee6_k6_restart_test.py','acee6_k6_cleanup_test.py','acee6_k6_functional_test.py')
for name in TESTS:
 r=subprocess.run([sys.executable,str(ROOT/name)],cwd=ROOT,text=True,capture_output=True,timeout=900);print(r.stdout,end='');assert r.returncode==0,(name,r.stdout,r.stderr)
print('ACEE6_K6_FAST_ACCEPTANCE_OK')
