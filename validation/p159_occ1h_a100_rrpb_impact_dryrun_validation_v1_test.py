from ontology.occ1h_a100_rrpb_impact_dryrun_validation import impact_and_validation
def test_functional(): r=impact_and_validation(); assert r["rrp5"]=="IMPACT_SURFACE_MAPPED" and r["rrp6"]=="DRY_RUN_ALL_PRODUCTS_VALID" and r["rrp7"]=="TRANSACTIONAL_INSTALLATION_COMPLETED" and r["rrp8"]=="VALIDATION_FUNNEL_PASSED"
def test_impact(): r=impact_and_validation(); assert len(r["impact_surface"])==4 and "transition from CIS to permanent sovereignty" in r["impact_surface"] and r["direct_consumers_checked"]
def test_degradation(): r=impact_and_validation(); assert r["current_verdict"]=="INCONCLUSIVE" and not r["transition_materialized"] and r["dependent_root_a105_not_opened"]
def test_nonregression(): r=impact_and_validation(); assert not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
