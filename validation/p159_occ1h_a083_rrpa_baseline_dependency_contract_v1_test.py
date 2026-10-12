from ontology.occ1h_a083_rrpa_baseline_dependency_contract import evidence
def test_rrpa_statuses():
 r=evidence(); assert [r["rrp0"],r["rrp1"],r["rrp2"],r["rrp3"],r["rrp4"]]==["BASELINE_FROZEN","DEPENDENCY_CLOSURE_ESTABLISHED","GAP_CAUSALLY_QUALIFIED","BASELINE_REPRODUCED","RESOLUTION_CONTRACT_FROZEN"] and r["fresh_interpreter_reproduction_count"]==2
def test_gap_preserved():
 r=evidence(); assert r["qualification"]=="RUNTIME_TOKEN_TO_CNP_BINDING_NOT_PROVEN" and r["applicability"]=="APPLICABILITY_UNDETERMINED" and r["verdict"]=="INCONCLUSIVE" and r["root"]
def test_degradation_fail_closed():
 r=evidence(); assert not r["token_to_cnp_runtime_binding_proven"] and r["false_promotion_forbidden"] and r["automatic_resolution_forbidden"] and not r["production_runtime_modified"]
def test_nonregression():
 r=evidence(); assert r["structural_group"]=="G5_LIFECYCLE_FRESHNESS_RUNTIME_BINDING" and r["resolution_category"]=="P160_BOUNDARY_CANDIDATE" and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
