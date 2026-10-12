import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'validation_artifacts/p159/occ1g/occ1g_closure_transaction_v1.json'
def load(): return json.loads(P.read_text(encoding='utf-8'))
def digest(o):
 x=dict(o); x.pop('transaction_id',None)
 return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def test_closure_transaction_integrity():
 o=load(); assert o['status']=='CLOSED'; assert o['milestone']=='OCC-1G'; assert o['transaction_id']==digest(o)
def test_closure_evidence_complete():
 o=load(); assert len(o['evidence_sha256'])==6; assert all(len(x)==64 for x in o['evidence_sha256'].values())
 assert o['closure_readiness']=='READY'; assert set(o['gcvi_status'].values())=={'PASS'}
def test_boundaries_preserved():
 o=load(); assert o['occ1h_opened'] is False and o['p160_opened'] is False and o['p159_final_lock'] is False
def test_functional_only():
 o=load(); assert o['functional_only'] is True and o['phenomenology_undetermined'] is True
