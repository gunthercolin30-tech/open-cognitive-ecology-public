from ontology.occ1h_a082_rrpc_root_materiality_disposition import disposition
def test_rrpc_materiality(): r=disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["root_materiality"]=="ROOT" and len(r["causal_chain"])==4
def test_elimination_exhausted(): r=disposition(); assert r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and not r["cache_to_cnp_binding_proven"] and not r["a082_specific_empirical_resistance_proven"]
def test_blocking_disposition(): r=disposition(); assert r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["verdict"]=="INCONCLUSIVE" and r["rrp_d_required"]
def test_nonregression(): r=disposition(); assert not r["criticality_changed"] and not r["production_runtime_modified"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
