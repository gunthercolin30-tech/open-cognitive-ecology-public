from ontology.occ1h_applicability_human_adoption_decision import human_adoption_decision

def test_exact_adoption():
 q=human_adoption_decision(); assert q["proposal_id"]=="P159-OCC1H-APPLICABILITY-AMENDMENT-V1"; assert q["decision"]=="ADOPT" and q["decision_source"]=="EXPLICIT_HUMAN_INPUT"; assert q["decision_recorded"] and q["decision_scope_exact"]

def test_existing_governance_path():
 q=human_adoption_decision(); assert q["action_class"]=="CONSTITUTIONAL_CHANGE"; assert q["authority_path"]=="EXISTING_P095_P106_GOVERNED_HUMAN_AUTHORITY"

def test_decision_is_not_application():
 q=human_adoption_decision(); assert not q["amendment_applied"]; assert not q["canonical_protocol_modified"]; assert not q["automatic_activation"] and not q["automatic_execution"]

def test_history_and_root_unchanged():
 q=human_adoption_decision(); assert not q["historical_verdicts_modified"] and q["A001_A105_history_preserved"]; assert not q["current_scenarios_reclassified"]; assert q["root_inconclusive_resolved"]==0 and q["global_root_inconclusive_baseline"]==29

def test_no_downstream_opening():
 q=human_adoption_decision(); assert not q["occ1h_closed"] and not q["occ1i_opened"] and not q["p159_final_lock"] and not q["p160_opened"]; assert q["functional_conclusion_only"] and q["phenomenology_undetermined"]
