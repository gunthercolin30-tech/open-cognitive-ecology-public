from ontology.occ1h_a084_rrpc_root_materiality_disposition import rrpc
def test_materiality(): r=rrpc(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["root_materiality"]=="ROOT" and len(r["causal_chain"])==4
def test_inconclusive_exhaustion(): r=rrpc(); assert r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and not r["clock_rollback_resistance_proven"]
def test_closure_disposition(): r=rrpc(); assert r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["verdict"]=="INCONCLUSIVE" and r["rrp_d_required"]
def test_nonregression(): r=rrpc(); assert not r["criticality_changed"] and not r["production_runtime_modified"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
