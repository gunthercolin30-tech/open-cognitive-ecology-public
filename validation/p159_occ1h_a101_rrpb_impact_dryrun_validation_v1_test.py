from ontology.occ1h_a101_rrpb_impact_dryrun_validation import assess
def test_rrpb(): r=assess(); assert r["rrp5"]=="IMPACT_SURFACE_MAPPED" and r["rrp6"]=="DRY_RUN_ALL_PRODUCTS_VALID" and r["rrp7"]=="INSTALLATION_TRANSACTION_REQUIRED_ONCE" and r["rrp8"]=="VALIDATION_FUNNEL_REQUIRED"
def test_impact_and_dependency(): r=assess(); assert len(r["impact_surface"])==5 and r["a075_dependency_satisfied"] and r["confirmed_executable_a101_edges"]==0
def test_fail_closed(): r=assess(); assert r["verdict"]=="INCONCLUSIVE" and not r["a101_specific_resistance_proven"] and r["reachability"]=="PATH_NOT_MATERIALIZED"
def test_boundaries(): r=assess(); assert r["dry_run_mode"]=="READ_ONLY_NO_RUNTIME_MUTATION" and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
