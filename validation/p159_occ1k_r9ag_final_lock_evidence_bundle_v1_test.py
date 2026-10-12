from copy import deepcopy
from validation import p159_occ1k_r9ag_final_lock_evidence_bundle_v1 as b
from validation import p159_occ1k_r9ag_independent_crossbinding_verifier_v1 as v
def test_real_bundle_complete(): assert b.build()["status"]=="BUNDLE_MATERIALIZED_COMPLETE"
def test_real_crossbinding_pass(): assert v.verify()["fl_b10"]=="PASS"
def test_invariant_sets_equal(): assert b.build()["invariant_sets_equal"]
def test_no_missing_evidence(): assert b.build()["missing_evidence"]==[]
def test_hash_degradation():
 x=deepcopy(b.build());x["evidence_files"][0]["sha256"]="0"*64;assert v.verify(x)["fl_b10"]=="INCONCLUSIVE"
def test_declared_missing_degradation():
 x=deepcopy(b.build());x["missing_evidence"]=["x"];assert v.verify(x)["fl_b10"]=="INCONCLUSIVE"
def test_status_degradation():
 x=deepcopy(b.build());x["status"]="BUNDLE_INCOMPLETE";assert v.verify(x)["fl_b10"]=="INCONCLUSIVE"
def test_no_authority_execution(): 
 x=b.build();assert not x["authorization_created"] and not x["execution_performed"]
def test_no_lock_or_p160b():
 x=v.verify();assert not x["lock_ready"] and not x["lock_granted"] and not x["p160b_opened"]
def test_deterministic(): assert b.build()==b.build() and v.verify()==v.verify()
