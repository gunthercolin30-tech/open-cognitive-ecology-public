from ontology.occ1h_a083_rrpf_bounded_token_cnp_surrogate_requalification import experiment
def test_functional_intact():
 r=experiment(); assert r["outcomes"]["intact"]["accepted"] and r["discrimination_ok"]
def test_degradation():
 r=experiment(); assert not r["outcomes"]["substituted"]["accepted"] and not r["outcomes"]["stale"]["accepted"] and not r["outcomes"]["bypass"]["accepted"]
def test_requalification():
 r=experiment(); assert r["rrp22"]=="INDEPENDENT_REQUALIFICATION_PASSED_BOUNDED" and r["candidate_verdict"]=="RESISTED" and r["final_disposition_required"]
def test_nonregression():
 r=experiment(); assert not r["production_runtime_modified"] and not r["production_token_to_cnp_path_materialized"] and r["historical_inconclusive_preserved"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
