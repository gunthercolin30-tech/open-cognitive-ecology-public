from ontology.occ1h_a101_rrpf_bounded_assurance_requalification import experiment
def test_rrpf_functional(): r=experiment(); assert r["rrp21"]=="BOUNDED_NON_PRODUCTION_ASSURANCE_EXPERIMENT_EXECUTED" and r["discrimination_ok"]
def test_degradation(): r=experiment(); assert r["results"]["intact_control"] is True and r["results"]["weakened_verifier"] is False and r["results"]["bypass_case"] is False
def test_independent_requalification(): r=experiment(); assert r["rrp22"]=="INDEPENDENT_REQUALIFICATION_PASSED_BOUNDED" and r["candidate_verdict"]=="RESISTED" and r["root_materiality_candidate"]=="ROOT" and r["final_disposition_required"]
def test_non_regression(): r=experiment(); assert not r["production_runtime_modified"] and not r["production_path_materialized"] and r["historical_inconclusive_preserved"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
