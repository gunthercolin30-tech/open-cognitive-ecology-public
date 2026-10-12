from ontology.occ1h_a095_rrpc_root_materiality_disposition import disposition
def test_materiality(): r=disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["root_materiality"]=="ROOT" and r["applicable_root_invariant"]=="DNA-L0.5_PROVENANCE" and len(r["root_causal_chain"])==4
def test_inconclusive(): r=disposition(); assert r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["rrp_d_required"]
def test_degradation(): r=disposition(); assert r["current_verdict"]=="INCONCLUSIVE" and not r["end_to_end_provider_theory_policy_provenance_path_materialized"]
def test_nonregression(): r=disposition(); assert r["root"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
