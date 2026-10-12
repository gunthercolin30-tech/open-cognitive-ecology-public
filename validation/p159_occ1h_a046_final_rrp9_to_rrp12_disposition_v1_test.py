from ontology.occ1h_a046_final_rrp9_to_rrp12_disposition import disposition
def test_final_disposition(): r=disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["rrp10"]=="INCONCLUSIVE_ELIMINATED" and r["rrp11"]=="CLOSURE_ELIGIBLE_FOR_A046_ONLY" and r["rrp12"]=="ROOT + RESOLVED_EMPIRICALLY" and r["final_verdict"]=="RESISTED"
def test_materiality(): r=disposition(); assert r["root_materiality"]=="ROOT" and r["root_invariants"]==["DNA.L0.2","DNA.L0.3","DNA.L0.5"] and not r["criticality_changed"]
def test_provenance_limits(): r=disposition(); assert r["historical_inconclusive_preserved"] and r["human_normative_decision_preserved"] and not r["real_runtime_path_claimed"]
def test_boundaries(): r=disposition(); assert not r["a046_blocks_occ1h"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
