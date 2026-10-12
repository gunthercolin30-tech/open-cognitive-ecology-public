from copy import deepcopy
from validation import p159_occ1k_r9af_fl_b1_b12_gate_reconciliation_v1 as a
def test_real_reconciliation(): 
 r=a.reconcile();assert r["pass_count"]==9 and r["remaining_blockers"]==["FL-B10","FL-B11","FL-B12"]
def test_b3_superseded_only():
 r=a.reconcile();assert r["gates"]["FL-B3"]["historical_verdict"]=="BLOCKED" and r["gates"]["FL-B3"]["current_verdict"]=="PASS"
def test_b10_not_promoted_without_bundle(): assert a.reconcile()["gates"]["FL-B10"]["current_verdict"]=="INCONCLUSIVE"
def test_b11_blocked_by_open_root_risk(): assert a.reconcile()["gates"]["FL-B11"]["current_verdict"]=="BLOCKED"
def test_b11_can_pass_only_when_registries_clear():
 rr={"items":[]};dd={"items":[]};assert a.reconcile(risk=rr,debt=dd)["gates"]["FL-B11"]["current_verdict"]=="PASS"
def test_b12_not_promoted_without_fresh_receipt(): assert a.reconcile()["gates"]["FL-B12"]["current_verdict"]=="INCONCLUSIVE"
def test_bad_r9ae_refused():
 e=deepcopy(a.load(a.R9AE));e["fl_b3"]="BLOCKED"
 try:a.reconcile(ae=e);assert False
 except RuntimeError:pass
def test_no_historical_rewrite():
 r=a.reconcile();assert not r["historical_r4_rewritten"] and not r["historical_risk_registry_rewritten"] and not r["historical_debt_registry_rewritten"]
def test_no_lock_or_p160b():
 r=a.reconcile();assert not r["lock_ready"] and not r["lock_granted"] and not r["p160b_opened"]
def test_deterministic(): assert a.reconcile()==a.reconcile()
