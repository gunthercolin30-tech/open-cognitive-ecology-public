from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
for n in ('acee6_k5_degradation_test.py','acee6_k5_report_tamper_test.py','acee6_k5_collision_fixture_test.py'):
 r=subprocess.run([sys.executable,str(ROOT/n)],cwd=ROOT,text=True,capture_output=True,timeout=300);print(r.stdout,end='');assert r.returncode==0,(n,r.stdout,r.stderr)
# One full campaign is sufficient for functional + non-regression.
r=subprocess.run([sys.executable,str(ROOT/'acee6_k5_functional_test.py')],cwd=ROOT,text=True,capture_output=True,timeout=900);print(r.stdout,end='');assert r.returncode==0,(r.stdout,r.stderr)
print('ACEE6_K5_FAST_ACCEPTANCE_OK')
