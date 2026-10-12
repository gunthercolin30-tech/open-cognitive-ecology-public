from copy import deepcopy
from validation import p159_occ1k_r9an_lock_ready_manifest_candidate_v1 as m
def test_real_candidate_lock_ready(): assert m.build("2026-09-30T00:00:00Z")["status"]=="LOCK_READY"
def test_required_manifest_fields():
 x=m.build("2026-09-30T00:00:00Z")
 for k in ("lock_id","milestone","lock_version","created_at","scope","source_tool_evidence_hashes","critical_invariants","blocking_criteria","limitations","residual_risks","status","manifest_hash"): assert k in x
def test_manifest_hash_self_consistent():
 x=m.build("2026-09-30T00:00:00Z"); h=x.pop("manifest_hash")
 import hashlib
 assert h==hashlib.sha256(m.canon(x).encode()).hexdigest()
def test_verifier_required(monkeypatch):
 orig=m.load
 def fake(p):
  x=deepcopy(orig(p))
  if p==m.V: x["status"]="REJECTED";x["lock_ready"]=False
  return x
 monkeypatch.setattr(m,"load",fake)
 assert m.build("2026-09-30T00:00:00Z")["status"]=="VALIDATION_PENDING"
def test_meta_required(monkeypatch):
 orig=m.load
 def fake(p):
  x=deepcopy(orig(p))
  if p==m.AJ: x["status"]="META_CROWN_INCONCLUSIVE"
  return x
 monkeypatch.setattr(m,"load",fake)
 assert m.build("2026-09-30T00:00:00Z")["status"]=="VALIDATION_PENDING"
def test_mut_fl_required(monkeypatch):
 orig=m.load
 def fake(p):
  x=deepcopy(orig(p))
  if p==m.AK: x["status"]="MUT_FL_FAIL"
  return x
 monkeypatch.setattr(m,"load",fake)
 assert m.build("2026-09-30T00:00:00Z")["status"]=="VALIDATION_PENDING"
def test_no_transition_receipt_yet(): assert m.build("2026-09-30T00:00:00Z")["transition_receipt_present"] is False
def test_no_runtime_activation(): assert m.build("2026-09-30T00:00:00Z")["runtime_active"] is False
def test_no_authority_execution_p160b():
 x=m.build("2026-09-30T00:00:00Z")
 assert not x["authority_created"] and not x["authorization_created"] and not x["execution_performed"] and not x["p160b_opened"]
def test_deterministic_with_fixed_timestamp(): assert m.build("2026-09-30T00:00:00Z")==m.build("2026-09-30T00:00:00Z")
