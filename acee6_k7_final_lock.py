from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
from acee6_k7_longitudinal_runner import EVIDENCE
from acee6_k7_report_verifier import verify_k7_report
ROOT=Path(__file__).resolve().parent
for name,timeout in (('acee6_k7_fast_acceptance_suite.py',3600),('acee6_k7_non_regression_test.py',3600)):
 r=subprocess.run([sys.executable,str(ROOT/name)],cwd=ROOT,text=True,capture_output=True,timeout=timeout);print(r.stdout,end='');assert r.returncode==0,(name,r.stdout,r.stderr)
assert EVIDENCE.is_file(),f'missing scientific evidence: {EVIDENCE}'
report=json.loads(EVIDENCE.read_text(encoding='utf-8'));v=verify_k7_report(report);assert v['valid'],v
assert report.get('public_schema_version')=='1.1.0'
for c in report['campaigns'].values():
 assert c['transaction_count']==1000 and c['segment_count']==10
 assert 'raw_hashes' in c and 'normalized_hashes' in c
print('ACEE6_K7_FINAL_LOCK_OK')
