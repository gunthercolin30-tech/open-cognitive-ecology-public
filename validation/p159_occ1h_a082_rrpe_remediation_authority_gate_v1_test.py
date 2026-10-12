from ontology.occ1h_a082_rrpe_remediation_authority_gate import authority_gate
def test_rrpe(): r=authority_gate(); assert r["rrp17"]=="BLOCKER_CAUSAL_DECOMPOSITION_COMPLETE" and r["rrp18"]=="TECHNICAL_ASSURANCE_CAPABILITY_GAP" and r["rrp19"]=="BOUNDED_NON_PRODUCTION_CACHE_TO_CNP_SURROGATE_ASSURANCE_DESIGN" and r["rrp20"]=="TECHNICAL_REMEDIATION_AUTHORIZED"
def test_no_normative_creation(): r=authority_gate(); assert not r["normative_gap_detected"] and r["normative_degrees_of_freedom"]==0 and not r["new_normative_decision_required"]
def test_minimality_and_barrier(): r=authority_gate(); assert all(r["minimality"].values()) and r["rrp_f_required"] and not r["remediation_executed"]
def test_nonregression(): r=authority_gate(); assert r["verdict"]=="INCONCLUSIVE" and r["root_materiality"]=="ROOT" and not r["production_runtime_modified"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
