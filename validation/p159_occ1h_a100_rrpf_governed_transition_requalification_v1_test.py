from ontology.occ1h_a100_rrpf_governed_transition_requalification import experiment
def test_rrp21():
 r=experiment(); assert r["rrp21_discrimination_ok"]; assert r["rrp21"]=="GOVERNED_D1_D2_BOUNDED_NON_PRODUCTION_EXPERIMENT_EXECUTED"
def test_rrp22_independent():
 r=experiment(); assert r["rrp22_discrimination_ok"]; assert r["rrp22"]=="INDEPENDENT_REQUALIFICATION_SUPPORTS_RETURN_TO_RRP9_12"; assert r["return_to_rrp9_12_required"]
def test_degradation():
 r=experiment(); assert all(v=="FAIL_CLOSED_TRANSITION_NOT_AUTHORIZED" for k,v in r["rrp22_results"].items() if k!="governed_control"); assert r["candidate_verdict"]=="RESISTED" and r["final_disposition_required"]
def test_nonregression():
 r=experiment(); assert r["historical_inconclusive_preserved"] and not r["canonical_constitution_modified"] and not r["production_runtime_modified"] and not r["production_transition_materialized"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
