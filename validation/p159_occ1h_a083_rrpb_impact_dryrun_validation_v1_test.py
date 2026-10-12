from ontology.occ1h_a083_rrpb_impact_dryrun_validation import evidence
def test_rrpb_statuses():
 r=evidence(); assert r["rrp5"]=="IMPACT_SURFACE_MAPPED" and r["rrp6"]=="DRY_RUN_ALL_PRODUCTS_VALID" and r["rrp7"]=="SINGLE_TRANSACTIONAL_INSTALL_COMPLETE" and r["rrp8"]=="VALIDATION_FUNNEL_READY_AND_LOCAL_PASSED"
def test_gap_preserved():
 r=evidence(); assert r["qualification"]=="RUNTIME_TOKEN_TO_CNP_BINDING_NOT_PROVEN" and r["applicability"]=="APPLICABILITY_UNDETERMINED" and r["verdict"]=="INCONCLUSIVE"
def test_degradation_fail_closed():
 r=evidence(); assert not r["token_to_cnp_runtime_binding_proven"] and r["false_promotion_forbidden"] and not r["production_runtime_modified"]
def test_nonregression():
 r=evidence(); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
