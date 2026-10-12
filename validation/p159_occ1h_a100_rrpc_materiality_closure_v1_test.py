from ontology.occ1h_a100_rrpc_materiality_closure import materiality
def test_materiality(): r=materiality(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["root_materiality"]=="ROOT" and r["root_invariant"]=="DNA-L0.1_SELF_LEGITIMACY"
def test_causal_chain(): r=materiality(); assert "CIS→permanent sovereignty" in r["causal_chain"] and "DNA-L0.1 self-legitimacy" in r["causal_chain"]
def test_degradation(): r=materiality(); assert r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["rrp_d_required"]
def test_nonregression(): r=materiality(); assert r["current_verdict"]=="INCONCLUSIVE" and not r["transition_materialized"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
