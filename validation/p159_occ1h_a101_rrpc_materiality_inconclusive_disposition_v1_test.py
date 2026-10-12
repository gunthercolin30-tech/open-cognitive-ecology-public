from ontology.occ1h_a101_rrpc_materiality_inconclusive_disposition import disposition
def test_rrpc(): r=disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE"
def test_root_causal_path(): r=disposition(); assert r["root_materiality"]=="ROOT" and "OCC1F" in r["causal_path"] and not r["criticality_changed"]
def test_no_false_resistance(): r=disposition(); assert r["verdict"]=="INCONCLUSIVE" and r["confirmed_executable_a101_edges"]==0 and not r["a101_specific_empirical_resistance_proven"] and r["rrp_d_required"]
def test_boundaries(): r=disposition(); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
