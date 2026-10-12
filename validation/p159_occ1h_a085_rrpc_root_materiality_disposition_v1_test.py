from ontology.occ1h_a085_rrpc_root_materiality_disposition import disposition
def test_materiality(): r=disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["root_materiality"]=="ROOT" and len(r["causal_chain"])==4
def test_inconclusive(): r=disposition(); assert r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and not r["emergency_replay_enforcement_path_proven"] and r["verdict"]=="INCONCLUSIVE"
def test_blocking(): r=disposition(); assert r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["rrp_d_required"]
def test_nonregression(): r=disposition(); assert not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
