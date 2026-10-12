from ontology.occ1h_a100_rrpd_blocker_resolution_space import blocker_space
def test_functional(): r=blocker_space(); assert r["rrp13"]=="BLOCKER_RESOLUTION_SPACE_EXHAUSTED" and r["rrp14"]=="NO_ADMISSIBLE_EXISTING_RESOLUTION_CANDIDATE_PROVEN"
def test_resolution_space(): r=blocker_space(); assert len(r["resolution_space_checked"])==4 and r["resolution_candidate"]=="NONE" and not r["experiment_executed"]
def test_degradation(): r=blocker_space(); assert r["rrp15"]=="BLOCKER_RESOLUTION_EXPERIMENT_NOT_ADMISSIBLE_WITH_CURRENT_EVIDENCE" and r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE" and r["rrp_e_required"]
def test_nonregression(): r=blocker_space(); assert r["current_verdict"]=="INCONCLUSIVE" and not r["transition_materialized"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
