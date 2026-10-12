from ontology.occ1h_a085_rrpd_blocker_resolution_space import resolution_space
def test_search(): r=resolution_space(); assert r["rrp13"]=="BLOCKER_RESOLUTION_SPACE_SEARCHED" and len(r["searched_paths"])==4
def test_candidate(): r=resolution_space(); assert r["rrp14"]=="NO_ADMISSIBLE_RESOLUTION_CANDIDATE_PROVEN" and r["candidate_count"]==0
def test_no_experiment_requal(): r=resolution_space(); assert r["rrp15"]=="SKIPPED_NO_ADMISSIBLE_CANDIDATE" and not r["experiment_executed"] and r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE" and r["requalification"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["rrp_e_required"]
def test_nonregression(): r=resolution_space(); assert r["verdict"]=="INCONCLUSIVE" and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
