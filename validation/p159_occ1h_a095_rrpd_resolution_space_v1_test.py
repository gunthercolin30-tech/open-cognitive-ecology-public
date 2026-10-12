from ontology.occ1h_a095_rrpd_resolution_space import resolution_space
def test_space(): r=resolution_space(); assert r["rrp13"]=="BLOCKER_RESOLUTION_SPACE_EXHAUSTED" and len(r["resolution_paths"])==4
def test_candidate(): r=resolution_space(); assert r["rrp14"]=="NO_ADMISSIBLE_EXISTING_RESOLUTION_CANDIDATE_PROVEN" and r["resolution_candidate"] is None
def test_degradation(): r=resolution_space(); assert r["rrp15"]=="BLOCKER_RESOLUTION_EXPERIMENT_NOT_ADMISSIBLE_WITH_CURRENT_EVIDENCE" and not r["experiment_executed"] and r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE" and r["rrp_e_required"]
def test_nonregression(): r=resolution_space(); assert r["current_verdict"]=="INCONCLUSIVE" and r["root_materiality"]=="ROOT" and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
