from ontology.occ1h_applicability_design_adversarial_crown import crown_evidence

def test_complete_precommitted_design_crown():
 q=crown_evidence(); assert q["attack_count"]==12 and len(q["attacks"])==12
 assert len({x["attack_id"] for x in q["attacks"]})==12
 assert all(x["success_criteria_fixed_before_execution"] is True for x in q["attacks"])
 assert all(x["result"]=="RESISTED_BY_DESIGN_CONSTRAINT" for x in q["attacks"])

def test_certificate_laundering_resisted():
 q=crown_evidence()
 for k in ("forged_certificate_rejected","absence_of_evidence_rejected","self_attestation_rejected","undetermined_promotion_without_proof_rejected"): assert q[k] is True

def test_binding_and_replay_resisted():
 q=crown_evidence()
 for k in ("hash_drift_invalidates_certificate","scenario_substitution_rejected","cross_state_replay_rejected","success_criteria_drift_invalidates_certificate"): assert q[k] is True

def test_root_verdict_and_authority_laundering_resisted():
 q=crown_evidence()
 for k in ("missing_certificate_blocks_root_closure","applicability_cannot_become_resisted_verdict","historical_verdict_rewrite_rejected","authority_laundering_rejected"): assert q[k] is True

def test_no_adoption_or_reclassification():
 q=crown_evidence()
 assert q["design_only"] is True and q["adoption_authorized"] is False and q["current_scenarios_reclassified"] is False
 assert q["root_inconclusive_resolved"]==0 and q["global_root_inconclusive_baseline"]==29
 for k in ("historical_verdicts_modified","success_criteria_modified","canonical_protocol_modified","normative_sources_modified","compiler_modified","authority_created","authorization_created","execution_created","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"): assert q[k] is False
 assert q["functional_conclusion_only"] is True and q["phenomenology_undetermined"] is True
