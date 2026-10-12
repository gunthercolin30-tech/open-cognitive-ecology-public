from copy import deepcopy
from validation import p159_occ1k_r9ap_apply_governed_lock_transition_v1 as m
TS="2026-09-30T00:00:00Z"
def test_real_transition_builds_locked():
 x=m.build_locked(TS);assert x["status"]=="LOCKED" and x["previous_status"]=="LOCK_READY"
def test_receipt_exactly_bound():
 x=m.build_locked(TS);r=m.load(m.R)
 assert x["governed_transition_receipt_sha256"]==m.sha(m.R)
 assert x["governed_transition_receipt_hash"]==r["receipt_hash"]
def test_bad_decision_fail_closed():
 r=deepcopy(m.load(m.R));r["decision"]="DENY_LOCK_TRANSITION"
 assert m.build_locked(TS,r=r) is None
def test_manifest_hash_mismatch_fail_closed():
 r=deepcopy(m.load(m.R));r["manifest_hash"]="0"*64
 assert m.build_locked(TS,r=r) is None
def test_bundle_hash_mismatch_fail_closed():
 r=deepcopy(m.load(m.R));r["evidence_bundle_hash"]="0"*64
 assert m.build_locked(TS,r=r) is None
def test_receipt_claiming_lock_fail_closed():
 r=deepcopy(m.load(m.R));r["receipt_is_lock"]=True
 assert m.build_locked(TS,r=r) is None
def test_no_runtime_activation():
 x=m.build_locked(TS);assert not x["runtime_active"] and not x["authorization_created"] and not x["execution_performed"]
def test_p160b_closed():
 assert m.build_locked(TS)["p160b_opened"] is False
def test_post_lock_not_preclaimed():
 x=m.build_locked(TS);assert not x["post_lock_verified"] and not x["global_post_lock_validation"]
def test_scope_limited():
 assert m.build_locked(TS)["lock_scope_claim"]=="P159/OCC-1 ONLY"
def test_deterministic_fixed_timestamp(): assert m.build_locked(TS)==m.build_locked(TS)
