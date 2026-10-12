from ontology.occ1h_a101_rrpd_blocker_resolution_space import resolution_space
def test_rrpd(): r=resolution_space(); assert r["rrp13"]=="BLOCKER_RESOLUTION_SPACE_SEARCHED" and r["rrp14"]=="NO_ADMISSIBLE_RESOLUTION_CANDIDATE_PROVEN" and r["rrp15"]=="SKIPPED_NO_ADMISSIBLE_CANDIDATE" and r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE"
def test_no_manufactured_candidate(): r=resolution_space(); assert r["candidate_count"]==0 and not r["experiment_executed"] and r["must_not_create_path_to_pass_test"]
def test_requalification(): r=resolution_space(); assert r["requalification"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["verdict"]=="INCONCLUSIVE" and r["rrp_e_required"]
def test_boundaries(): r=resolution_space(); assert not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
