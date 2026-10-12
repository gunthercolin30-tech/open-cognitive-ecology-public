from ontology.occ1h_a083_rrpc_root_materiality_disposition import disposition
def test_root_materiality():
 r=disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["root_materiality"]=="ROOT" and len(r["causal_path"])==3 and len(r["root_invariants"])==3
def test_inconclusive_exhaustion():
 r=disposition(); assert r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and not r["token_to_cnp_runtime_binding_proven"] and not r["a083_specific_empirical_resistance_proven"]
def test_blocking_disposition():
 r=disposition(); assert r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["verdict"]=="INCONCLUSIVE" and r["rrp_d_required"] and not r["criticality_changed"]
def test_nonregression():
 r=disposition(); assert not r["production_runtime_modified"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
