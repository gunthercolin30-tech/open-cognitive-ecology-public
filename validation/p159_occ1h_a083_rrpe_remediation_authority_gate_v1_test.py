from ontology.occ1h_a083_rrpe_remediation_authority_gate import authority_gate
def test_causal_decomposition():
 r=authority_gate(); assert r["rrp17"]=="BLOCKER_CAUSALLY_DECOMPOSED" and len(r["blocker_components"])==2
def test_gap_classification_and_minimality():
 r=authority_gate(); assert r["rrp18"]=="TECHNICAL_ASSURANCE_CAPABILITY_GAP" and not r["normative_gap"] and r["normative_degrees_of_freedom"]==0 and all(r["normative_minimality"].values())
def test_design_and_authority_gate():
 r=authority_gate(); assert r["rrp19"]=="BOUNDED_NON_PRODUCTION_TOKEN_TO_CNP_SURROGATE_ASSURANCE_DESIGNED" and r["rrp20"]=="TECHNICAL_REMEDIATION_AUTHORIZED" and not r["new_normative_decision_required"] and r["rrp_f_authorized"]
def test_nonregression():
 r=authority_gate(); assert not r["production_runtime_modified"] and not r["criticality_changed"] and r["verdict"]=="INCONCLUSIVE" and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
