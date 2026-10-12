from copy import deepcopy
from validation import p159_occ1k_r9as_exhaustive_closure_certification_v1 as m
def test_real_closure_certified():
 x=m.certify();assert x["status"]=="P159_EXHAUSTIVE_CLOSURE_CERTIFIED" and x["passed"]==x["total"]==10
def test_locked_required():
 x=deepcopy(m.load(m.L));x["status"]="LOCK_DEGRADED"
 assert "NOT_CERTIFIED" in m.certify({"locked":x})["status"]
def test_exact_scope_required():
 x=deepcopy(m.load(m.L));x["lock_scope_claim"]="P159+"
 assert "NOT_CERTIFIED" in m.certify({"locked":x})["status"]
def test_post_lock_verifier_required():
 x=deepcopy(m.load(m.Q));x["status"]="REJECTED"
 assert "NOT_CERTIFIED" in m.certify({"post":x})["status"]
def test_post_lock_exact_count_required():
 x=deepcopy(m.load(m.Q));x["passed"]=15
 assert "NOT_CERTIFIED" in m.certify({"post":x})["status"]
def test_global_validation_required():
 assert "NOT_CERTIFIED" in m.certify({"report":"validation_mode=fast_acceptance"})["status"]
def test_bundle_required():
 x=deepcopy(m.load(m.B));x["status"]="INCOMPLETE"
 assert "NOT_CERTIFIED" in m.certify({"bundle":x})["status"]
def test_runtime_must_remain_inactive():
 x=deepcopy(m.load(m.L));x["runtime_active"]=True
 assert "NOT_CERTIFIED" in m.certify({"locked":x})["status"]
def test_p160b_stays_closed_during_certification():
 x=m.certify();assert not x["p160b_opened"]
def test_functional_scope_only():
 x=m.certify();assert x["claim_scope"]=="FUNCTIONAL P159/OCC-1 ONLY"
def test_read_only_certification():
 assert m.certify()["production_modified"] is False
def test_deterministic(): assert m.certify()==m.certify()
