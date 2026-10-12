from copy import deepcopy
import hashlib
from validation import p159_occ1k_r9ao2_schema_aware_governed_final_lock_transition_receipt_v2 as m
TS="2026-09-30T00:00:00Z"

def test_real_receipt_complete_and_approved():
    x=m.build(TS); assert x["decision"]=="APPROVE_LOCK_TRANSITION"; assert x["canonical_fields_complete"]

def test_bundle_hash_is_external_artifact_sha():
    x=m.build(TS); assert x["evidence_bundle_hash"]==m.sha(m.B)
    assert x["evidence_bundle_hash"]=="26698395f50a7b4b8383e759da4449a0096a13d6c9ae9a0ac529b05b54915b2f"

def test_all_canonical_fields_nonempty():
    x=m.build(TS); assert all(x[k] not in (None,"") for k in m.REQUIRED)

def test_missing_bundle_hash_denies():
    x=m.build(TS,{"bundle_artifact_sha256":""})
    assert x["decision"]=="DENY_LOCK_TRANSITION" and not x["eligible_for_transition"]

def test_lock_ready_required():
    a=deepcopy(m.load(m.M)); a["status"]="VALIDATION_PENDING"
    assert m.build(TS,{"manifest":a})["decision"]=="DENY_LOCK_TRANSITION"

def test_verifier_required():
    a=deepcopy(m.load(m.V)); a["status"]="REJECTED"; a["lock_ready"]=False
    assert m.build(TS,{"verifier":a})["decision"]=="DENY_LOCK_TRANSITION"

def test_bundle_complete_required():
    a=deepcopy(m.load(m.B)); a["status"]="BUNDLE_INCOMPLETE"
    assert m.build(TS,{"bundle":a})["decision"]=="DENY_LOCK_TRANSITION"

def test_historical_r9ao_preserved():
    x=m.build(TS); assert x["historical_r9ao_preserved"] and not x["historical_r9ao_rewritten"]

def test_receipt_not_lock():
    x=m.build(TS); assert not x["receipt_is_lock"] and not x["lock_applied"]

def test_no_runtime_authority_execution_p160b():
    x=m.build(TS)
    assert not x["runtime_active"] and not x["authority_created"] and not x["authorization_created"]
    assert not x["execution_performed"] and not x["p160b_opened"]

def test_receipt_hash_self_consistent():
    x=m.build(TS); h=x.pop("receipt_hash")
    assert h==hashlib.sha256(m.canon(x).encode()).hexdigest()

def test_deterministic_fixed_timestamp(): assert m.build(TS)==m.build(TS)
