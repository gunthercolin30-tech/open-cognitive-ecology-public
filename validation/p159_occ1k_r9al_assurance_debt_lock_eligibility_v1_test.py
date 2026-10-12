from copy import deepcopy
from validation import p159_occ1k_r9al_assurance_debt_lock_eligibility_v1 as a
def test_real_debt_resolved(): assert a.evaluate()["superseding_debt_assessment"]["status"]=="RESOLVED_BY_SUPERSEDING_EVIDENCE"
def test_historical_debt_preserved(): assert a.evaluate()["historical_debt"]["status"]=="OPEN" and not a.evaluate()["historical_debt"]["rewritten"]
def test_meta_required():
 j=deepcopy(a.load(a.AJ));j["failed"]=1;assert a.evaluate(aj=j)["lock_eligibility"]=="BLOCKED"
def test_mut_fl_required():
 k=deepcopy(a.load(a.AK));k["mroot_survived"]=1;assert a.evaluate(ak=k)["lock_eligibility"]=="BLOCKED"
def test_no_contamination_required():
 k=deepcopy(a.load(a.AK));k["baseline_contaminated"]=True;assert a.evaluate(ak=k)["lock_eligibility"]=="BLOCKED"
def test_b12_required():
 i=deepcopy(a.load(a.AI));i["fl_b12"]="INCONCLUSIVE";assert a.evaluate(ai=i)["lock_eligibility"]=="BLOCKED"
def test_independent_verifier_not_claimed(): assert a.evaluate()["independent_final_lock_verifier_complete"] is False
def test_transition_not_claimed(): assert a.evaluate()["transition_receipt_complete"] is False
def test_no_lock_or_p160b():
 x=a.evaluate();assert not x["lock_ready"] and not x["lock_granted"] and not x["p160b_opened"]
def test_deterministic(): assert a.evaluate()==a.evaluate()
