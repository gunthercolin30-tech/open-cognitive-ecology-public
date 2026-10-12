from copy import deepcopy
from pathlib import Path
from ontology import occ_p159_final_lock as fl
ROOT=Path(__file__).resolve().parents[1]
def test_eligibility_green_non_authorizing():
 x=fl.evaluate_eligibility(ROOT);assert x["status"]=="ELIGIBLE",[k for k,v in x["checks"].items() if v is not True];assert x["p159_final_lock"] is False and x["p160_opened"] is False
def test_blocked_cannot_lock():
 x=fl.evaluate_eligibility(ROOT);x["status"]="BLOCKED"
 try:fl.build_lock(x,"0"*64)
 except ValueError:return
 raise AssertionError
def test_lock_deterministic():
 x=fl.evaluate_eligibility(ROOT);assert fl.build_lock(x,"1"*64)==fl.build_lock(x,"1"*64)
def test_lock_boundary():
 x=fl.build_lock(fl.evaluate_eligibility(ROOT),"2"*64);assert x["p159_final_lock"] is True and x["p160_opened"] is False and x["authorization_created"] is False and x["execution_performed"] is False
def test_tamper_changes_identity():
 x=fl.build_lock(fl.evaluate_eligibility(ROOT),"3"*64);bad=deepcopy(x);bad["p160_opened"]=True;assert fl.objhash({k:v for k,v in bad.items() if k!="final_lock_identity_sha256"})!=x["final_lock_identity_sha256"]
def test_validation_receipt_is_bound():
 e=fl.evaluate_eligibility(ROOT);assert fl.build_lock(e,"4"*64)["final_lock_identity_sha256"]!=fl.build_lock(e,"5"*64)["final_lock_identity_sha256"]
