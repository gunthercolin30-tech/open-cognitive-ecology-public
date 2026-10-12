from copy import deepcopy
import hashlib
from validation import p159_occ1k_r9ao_governed_final_lock_transition_receipt_v1 as m

TS="2026-09-30T00:00:00Z"

def test_real_receipt_approves_transition():
    x=m.build(TS)
    assert x["decision"]=="APPROVE_LOCK_TRANSITION"
    assert x["eligible_for_transition"] is True

def test_canonical_receipt_fields():
    x=m.build(TS)
    for k in ("lock_id","manifest_hash","previous_baseline","new_baseline","authority","decision","timestamp","reason","evidence_bundle_hash"):
        assert k in x and x[k] not in (None,"")

def test_manifest_hash_exactly_bound():
    x=m.build(TS); src=m.load(m.M)
    assert x["manifest_hash"]==src["manifest_hash"]
    assert x["manifest_artifact_sha256"]==m.sha(m.M)

def test_bundle_exactly_bound():
    x=m.build(TS); b=m.load(m.B)
    assert x["evidence_bundle_hash"]==b["bundle_sha256"]
    assert x["evidence_bundle_artifact_sha256"]==m.sha(m.B)

def test_lock_ready_required(monkeypatch):
    orig=m.load
    def fake(p):
        x=deepcopy(orig(p))
        if p==m.M: x["status"]="VALIDATION_PENDING"
        return x
    monkeypatch.setattr(m,"load",fake)
    assert m.build(TS)["decision"]=="DENY_LOCK_TRANSITION"

def test_independent_verifier_required(monkeypatch):
    orig=m.load
    def fake(p):
        x=deepcopy(orig(p))
        if p==m.V: x["status"]="REJECTED"; x["lock_ready"]=False
        return x
    monkeypatch.setattr(m,"load",fake)
    assert m.build(TS)["decision"]=="DENY_LOCK_TRANSITION"

def test_bundle_required(monkeypatch):
    orig=m.load
    def fake(p):
        x=deepcopy(orig(p))
        if p==m.B: x["status"]="BUNDLE_INCOMPLETE"
        return x
    monkeypatch.setattr(m,"load",fake)
    assert m.build(TS)["decision"]=="DENY_LOCK_TRANSITION"

def test_receipt_is_not_lock():
    x=m.build(TS)
    assert x["receipt_is_lock"] is False and x["lock_applied"] is False

def test_no_runtime_authority_execution_p160b():
    x=m.build(TS)
    assert not x["runtime_active"]
    assert not x["authority_created"]
    assert not x["authorization_created"]
    assert not x["execution_performed"]
    assert not x["p160b_opened"]

def test_receipt_hash_self_consistent():
    x=m.build(TS); h=x.pop("receipt_hash")
    assert h==hashlib.sha256(m.canon(x).encode()).hexdigest()

def test_deterministic_fixed_timestamp():
    assert m.build(TS)==m.build(TS)
