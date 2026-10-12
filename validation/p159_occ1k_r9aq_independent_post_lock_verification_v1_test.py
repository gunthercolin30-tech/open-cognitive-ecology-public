from copy import deepcopy
from validation import p159_occ1k_r9aq_independent_post_lock_verification_v1 as m
def test_real_lock_verified():
 x=m.verify();assert x["status"]=="VERIFIED" and x["passed"]==x["total"]
def test_all_checks_executed(): assert m.verify()["total"]==16
def test_locked_status_required():
 x=deepcopy(m.load(m.L));x["status"]="LOCK_READY"
 assert m.verify({"locked":x})["status"]=="REJECTED"
def test_locked_self_hash_required():
 x=deepcopy(m.load(m.L));x["scope"]="tampered"
 assert m.verify({"locked":x})["status"]=="REJECTED"
def test_scope_exact():
 x=deepcopy(m.load(m.L));x["lock_scope_claim"]="P159+"
 assert m.verify({"locked":x})["status"]=="REJECTED"
def test_receipt_semantic_binding():
 x=deepcopy(m.load(m.R));x["receipt_hash"]="0"*64
 assert m.verify({"receipt":x})["status"]=="REJECTED"
def test_application_source_binding():
 x=deepcopy(m.load(m.A));x["source_manifest_sha256"]="0"*64
 assert m.verify({"application":x})["status"]=="REJECTED"
def test_application_receipt_binding():
 x=deepcopy(m.load(m.A));x["transition_receipt_sha256"]="0"*64
 assert m.verify({"application":x})["status"]=="REJECTED"
def test_application_locked_binding():
 x=deepcopy(m.load(m.A));x["locked_manifest_hash"]="0"*64
 assert m.verify({"application":x})["status"]=="REJECTED"
def test_receipt_approval_required():
 x=deepcopy(m.load(m.R));x["decision"]="DENY_LOCK_TRANSITION"
 assert m.verify({"receipt":x})["status"]=="REJECTED"
def test_runtime_must_remain_inactive():
 x=deepcopy(m.load(m.L));x["runtime_active"]=True
 assert m.verify({"locked":x})["status"]=="REJECTED"
def test_p160b_must_remain_closed():
 x=deepcopy(m.load(m.L));x["p160b_opened"]=True
 assert m.verify({"locked":x})["status"]=="REJECTED"
def test_verifier_never_repairs():
 x=m.verify();assert not x["repairs_performed"] and not x["locked_artifact_modified"]
def test_global_validation_not_preclaimed(): assert m.verify()["global_post_lock_validation"] is False
def test_deterministic(): assert m.verify()==m.verify()
