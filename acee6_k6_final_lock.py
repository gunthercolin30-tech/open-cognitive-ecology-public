from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
from acee6_k6_longitudinal_runner import EVIDENCE
from acee6_k6_report_verifier import verify_report
ROOT=Path(__file__).resolve().parent
for name,timeout in (('acee6_k6_fast_acceptance_suite.py',1800),('acee6_k6_non_regression_test.py',1800)):
 r=subprocess.run([sys.executable,str(ROOT/name)],cwd=ROOT,text=True,capture_output=True,timeout=timeout);print(r.stdout,end='');assert r.returncode==0,(name,r.stdout,r.stderr)
assert EVIDENCE.is_file(),f'missing scientific evidence: {EVIDENCE}'
report=json.loads(EVIDENCE.read_text(encoding='utf-8'));v=verify_report(report);assert v['valid'],v;assert report['transaction_count']==1000;assert report['segment_count']==10;assert report['committed_count']==500
print('ACEE6_K6_FINAL_LOCK_OK')
