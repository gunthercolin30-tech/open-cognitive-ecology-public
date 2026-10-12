import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'validation_artifacts/p159/occ1g'
P=A/'occ1g_postclose_verification_v1.json'
C=A/'occ1g_closure_transaction_v1.json'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def digest(o):
 x=dict(o); x.pop('proof_sha256',None)
 return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def test_postclose_proof_integrity():
 p=load(P); assert p['status']=='POSTCLOSE_VERIFIED'; assert p['proof_sha256']==digest(p)
def test_closure_transaction_binding():
 p=load(P); c=load(C); assert p['closure_transaction_id']==c['transaction_id']
 assert p['closure_artifact_sha256']==hashlib.sha256(C.read_bytes()).hexdigest()
def test_evidence_rehashed():
 p=load(P); c=load(C)
 for n,h in c['evidence_sha256'].items(): assert hashlib.sha256((A/n).read_bytes()).hexdigest()==h==p['verified_evidence_sha256'][n]
def test_boundaries_and_epistemics():
 p=load(P); assert p['occ1g_closed'] is True and p['occ1g_postclose_verified'] is True
 assert p['occ1h_opened'] is False and p['p160_opened'] is False and p['p159_final_lock'] is False
 assert p['functional_only'] is True and p['phenomenology_undetermined'] is True
