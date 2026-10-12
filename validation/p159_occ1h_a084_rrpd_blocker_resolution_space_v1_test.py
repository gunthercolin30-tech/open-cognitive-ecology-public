from ontology.occ1h_a084_rrpd_blocker_resolution_space import rrpd
def test_search(): r=rrpd(); assert r["rrp13"]=="BLOCKER_RESOLUTION_SPACE_SEARCHED" and len(r["searched_paths"])==4
def test_candidate_proof(): r=rrpd(); assert r["candidate_count"]==0 and r["rrp14"]=="NO_ADMISSIBLE_RESOLUTION_CANDIDATE_PROVEN"
def test_no_experiment_and_requalification(): r=rrpd(); assert r["rrp15"]=="SKIPPED_NO_ADMISSIBLE_CANDIDATE" and not r["experiment_executed"] and r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE" and r["rrp_e_required"]
def test_nonregression(): r=rrpd(); assert r["requalification"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["verdict"]=="INCONCLUSIVE" and not r["production_path_created"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
