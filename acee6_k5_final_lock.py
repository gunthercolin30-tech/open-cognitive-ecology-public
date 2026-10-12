from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
from acee6_k5_transaction_runner import EVIDENCE,verify
ROOT=Path(__file__).resolve().parent
r=subprocess.run([sys.executable,str(ROOT/'acee6_k50_final_lock.py')],cwd=ROOT,text=True,capture_output=True,timeout=900);print(r.stdout,end='');assert r.returncode==0,(r.stdout,r.stderr)
r=subprocess.run([sys.executable,str(ROOT/'acee6_k5_fast_acceptance_suite.py')],cwd=ROOT,text=True,capture_output=True,timeout=1200);print(r.stdout,end='');assert r.returncode==0,(r.stdout,r.stderr)
assert EVIDENCE.is_file(),EVIDENCE
report=json.loads(EVIDENCE.read_text(encoding='utf-8'));v=verify(report);assert v['valid'],v;assert report['transaction_count']==100;assert report['committed_count']==50
print('ACEE6_K5_FINAL_LOCK_OK')
