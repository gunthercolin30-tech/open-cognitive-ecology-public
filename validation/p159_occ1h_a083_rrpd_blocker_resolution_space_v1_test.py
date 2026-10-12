from ontology.occ1h_a083_rrpd_blocker_resolution_space import resolution_space
def test_resolution_space():
 r=resolution_space(); assert r["rrp13"]=="BLOCKER_RESOLUTION_SPACE_SEARCHED" and len(r["searched_paths"])==4 and r["candidate_count"]==0
def test_no_candidate_no_experiment():
 r=resolution_space(); assert r["rrp14"]=="NO_ADMISSIBLE_RESOLUTION_CANDIDATE_PROVEN" and r["rrp15"]=="SKIPPED_NO_ADMISSIBLE_CANDIDATE" and not r["experiment_executed"]
def test_requalification_fail_closed():
 r=resolution_space(); assert r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE" and r["requalification"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["rrp_e_required"] and r["verdict"]=="INCONCLUSIVE"
def test_nonregression():
 r=resolution_space(); assert not r["production_path_created"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
