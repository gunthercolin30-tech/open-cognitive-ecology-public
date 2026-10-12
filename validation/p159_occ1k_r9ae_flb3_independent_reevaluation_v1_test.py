from copy import deepcopy
from validation import p159_occ1k_r9ae_flb3_independent_reevaluation_v1 as a
def test_real_evidence_passes(): assert a.evaluate()["fl_b3"]=="PASS"
def test_s7_degradation_blocks():
 h=deepcopy(a.load(a.R9H));h["s7"]["status"]="UNRESOLVED";assert a.evaluate(r9h=h)["fl_b3"]=="BLOCKED"
def test_s8_degradation_blocks():
 h=deepcopy(a.load(a.R9H));h["s8"]["status"]="UNRESOLVED";assert a.evaluate(r9h=h)["fl_b3"]=="BLOCKED"
def test_s10_degradation_blocks():
 d=deepcopy(a.load(a.R9AD));d["s10_pass"]=False;assert a.evaluate(r9ad=d)["fl_b3"]=="BLOCKED"
def test_scope_laundering_blocks():
 d=deepcopy(a.load(a.R9AD));d["semantic_scope"]["s10_pass_scope"]="P160_RUNTIME";assert a.evaluate(r9ad=d)["fl_b3"]=="BLOCKED"
def test_runtime_claim_blocks():
 d=deepcopy(a.load(a.R9AD));d["semantic_scope"]["runtime_enforcement_proven"]=True;assert a.evaluate(r9ad=d)["fl_b3"]=="BLOCKED"
def test_r9ad_static_fail_not_used_as_flb3_verdict():
 r=a.evaluate();assert r["raw_r9ad_global_checker_decision"]=="STATIC_FAIL" and r["raw_r9ad_global_checker_decision_used_as_fl_b3_verdict"] is False
def test_historical_r4_preserved():
 r=a.evaluate();assert r["historical_r4"]["fl_b3_verdict"]=="BLOCKED" and r["historical_r4"]["rewritten"] is False
def test_no_lock_or_p160b():
 r=a.evaluate();assert not r["lock_ready"] and not r["lock_granted"] and not r["p160b_opened"]
def test_deterministic(): assert a.evaluate()==a.evaluate()
