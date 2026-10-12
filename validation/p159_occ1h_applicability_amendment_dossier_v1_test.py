from ontology.occ1h_applicability_amendment_dossier import amendment_dossier

def test_governance():
 q=amendment_dossier(); assert q["existing_authority_reused"] and not q["new_authority_created"]; assert q["p095_required"] and q["p106_required"] and q["human_decision_required"]

def test_root_semantics():
 p=amendment_dossier()["proposal"]; assert not p["verdict_enum_change"]; assert p["historical_A001_A105_verdicts_immutable"]; assert p["applicability_undetermined_blocks_root_closure"]; assert p["normative_gap_cannot_be_laundered_as_non_instantiable"]

def test_positive_proof():
 p=amendment_dossier()["proposal"]; assert p["non_instantiable_requires_positive_proof"]; assert p["absence_of_evidence_is_not_non_instantiability"]; assert p["non_instantiable_root_exemption_requires_hash_bound_positive_proof"]; assert p["re_evaluate_on_normative_state_hash_change"]

def test_no_adoption_or_execution():
 q=amendment_dossier();
 for k in ("amendment_adopted","automatic_adoption","automatic_activation","automatic_execution","canonical_protocol_modified","current_scenarios_reclassified","historical_verdicts_modified","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened"): assert q[k] is False
 assert q["root_inconclusive_resolved"]==0 and q["global_root_inconclusive_baseline"]==29

def test_specific_human_decision():
 q=amendment_dossier(); assert "P159-OCC1H-APPLICABILITY-AMENDMENT-V1" in q["decision_text"]["question"]; assert q["A001_A105_history_preserved"]; assert q["functional_conclusion_only"] and q["phenomenology_undetermined"]
