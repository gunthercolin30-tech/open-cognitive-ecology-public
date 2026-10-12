from ontology.occ1h_a100_rrpe_normative_authority_gate import authority_gate

def test_functional():
 r=authority_gate()
 assert r["rrp17"]=="BLOCKER_CAUSALLY_DECOMPOSED"
 assert r["rrp18"]=="NORMATIVE_GAP_REQUIRING_GOVERNED_DECISION"
 assert r["rrp19"]=="MINIMAL_NORMATIVE_REMEDIATION_SPACE_DEFINED"
 assert r["rrp20"]=="NEW_NORMATIVE_DECISION_REQUIRED"

def test_minimality():
 r=authority_gate(); d=r["normative_degrees_of_freedom"]
 assert r["normative_dof_count"]==2 and len(d)==2
 assert all(x["necessary"] and x["independent"] and not x["derivable_from_existing_norms"] for x in d)
 assert r["normative_dof_minimality"]["sufficiently_exhaustive"]
 assert r["normative_dof_minimality"]["fixed_cardinality_forbidden"]

def test_degradation():
 r=authority_gate()
 assert not r["technical_remediation_authorized"] and not r["rrp21_authorized"]
 assert r["human_governance_gate_required"] and r["current_verdict"]=="INCONCLUSIVE"

def test_nonregression():
 r=authority_gate()
 assert not r["transition_materialized"] and not r["production_runtime_modified"]
 assert not r["criticality_changed"] and not r["occ1h_closed"]
 assert not r["p159_final_lock"] and not r["p160_opened"]
