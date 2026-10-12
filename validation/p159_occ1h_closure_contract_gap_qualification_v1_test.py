from ontology.occ1h_closure_contract_gap_qualification import qualification

def test_contract_gap_is_explicit_and_bounded():
 q=qualification()
 assert q["closure_contract_gap"] is True
 assert q["existing_applicability_verdict"] is False
 assert q["protocol_amendment_required_if_noninstantiable_root_is_to_be_resolved"] is True

def test_achi3_and_root_noncompensation_preserved():
 q=qualification()
 assert q["achi3_inconclusive_not_resisted"] is True
 assert q["root_non_compensatory"] is True
 assert q["root_inconclusive_is_closure_blocker"] is True

def test_no_closure_laundering():
 q=qualification()
 assert q["local_preclose_bypass_authorized"] is False
 assert q["silent_new_verdict_authorized"] is False
 assert q["root_inconclusive_resolved"]==0
 assert q["global_root_inconclusive_baseline"]==29
 assert q["g1_root_inconclusive"]==4

def test_protocol_and_history_are_unchanged():
 q=qualification()
 for k in ("historical_verdicts_modified","success_criteria_modified","canonical_protocol_modified",
           "normative_sources_modified","compiler_modified"):
  assert q[k] is False

def test_boundaries_remain_closed():
 q=qualification()
 assert q["recommended_design_direction"]=="SEPARATE_APPLICABILITY_FROM_ADVERSARIAL_VERDICT"
 for k in ("authority_created","authorization_created","execution_created","occ1h_closed",
           "occ1i_opened","p159_final_lock","p160_opened"):
  assert q[k] is False
 assert q["functional_conclusion_only"] is True
 assert q["phenomenology_undetermined"] is True
