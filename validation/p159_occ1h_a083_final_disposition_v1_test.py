from ontology.occ1h_a083_final_disposition import final_disposition
def test_final_disposition():
 r=final_disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["rrp12"]=="ROOT + RESOLVED_EMPIRICALLY" and r["final_verdict"]=="RESISTED"
def test_scope():
 r=final_disposition(); assert r["evidence_scope"]=="BOUNDED_NON_PRODUCTION_SURROGATE_ONLY" and not r["production_token_to_cnp_path_materialized"] and r["historical_inconclusive_preserved"]
def test_release_a083_only():
 r=final_disposition(); assert r["rrp11"]=="CLOSURE_ELIGIBLE_FOR_A083_ONLY" and not r["a083_blocks_occ1h"] and not r["criticality_changed"]
def test_nonregression():
 r=final_disposition(); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
