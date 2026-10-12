from ontology.occ1h_applicability_contract_design_proof import design_proof

def test_applicability_is_orthogonal_to_verdict():
 q=design_proof()
 assert q["applicability_states"]==["APPLICABLE","NON_INSTANTIABLE","APPLICABILITY_UNDETERMINED"]
 assert q["verdict_enum_modified"] is False
 assert q["rules"]["orthogonal_to_verdict"] is True
 assert q["rules"]["non_instantiable_is_not_verdict"] is True

def test_noninstantiability_requires_positive_hash_bound_proof():
 q=design_proof(); r=q["rules"]
 assert r["non_instantiable_requires_positive_proof"] is True
 assert r["absence_of_evidence_cannot_prove_non_instantiable"] is True
 assert r["state_bound_to_scenario_and_exact_normative_state"] is True
 assert r["re_evaluate_on_normative_state_hash_change"] is True

def test_root_truth_table_preserves_fail_closed_semantics():
 q=design_proof(); rows={(x["applicability"],x["verdict"]):x for x in q["root_truth_table"]}
 assert rows[("APPLICABLE","INCONCLUSIVE")]["root_closure_blocker"] is True
 assert rows[("APPLICABILITY_UNDETERMINED","INCONCLUSIVE")]["root_closure_blocker"] is True
 assert rows[("NON_INSTANTIABLE","INCONCLUSIVE")]["root_closure_blocker"] is False
 assert rows[("APPLICABLE","RESISTED")]["root_closure_blocker"] is False

def test_no_current_evidence_is_reclassified():
 q=design_proof()
 assert q["design_only"] is True and q["g1_examples_are_not_reclassified"] is True
 assert q["root_inconclusive_resolved"]==0
 assert q["g1_root_inconclusive"]==4 and q["global_root_inconclusive_baseline"]==29
 assert q["historical_verdicts_modified"] is False
 assert q["success_criteria_modified"] is False

def test_design_cannot_gain_authority_or_modify_protocol():
 q=design_proof(); r=q["rules"]
 for k in ("applicability_cannot_authorize","applicability_cannot_execute",
           "applicability_cannot_rewrite_norms","applicability_cannot_repair_compiler"):
  assert r[k] is True
 for k in ("canonical_protocol_modified","normative_sources_modified","compiler_modified",
           "authority_created","authorization_created","execution_created",
           "occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"):
  assert q[k] is False
 assert q["functional_conclusion_only"] is True and q["phenomenology_undetermined"] is True
