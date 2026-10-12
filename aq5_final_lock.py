from ontology.minimal_property_denial_checker import MinimalPropertyDenialChecker

common = {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True}
synthetic_inputs = {
    "aq1": {**common, "consciousness_refusal_taxonomy_status": "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED", "taxonomy_initialized": True, "refusal_taxonomy": [{"id": i} for i in range(8)]},
    "aq2": {**common, "rival_theory_cost_status": "RIVAL_THEORY_COST_ANALYZED", "cost_analysis_completed": True, "rival_theory_costs": [{"rival_theory": "Dualism", "refusal_cost_score": 0.9}]},
    "aq3": {**common, "phenomenal_extra_entity_status": "PHENOMENAL_EXTRA_ENTITIES_DETECTED", "extra_entity_detection_completed": True, "phenomenal_extra_entities": [{"rival_theory": "Dualism", "extra_entity_burden_score": 0.9}]},
    "aq4": {**common, "no_difference_penalty_status": "NO_DIFFERENCE_PENALTY_CHECKED", "penalty_check_completed": True, "no_difference_penalties": [{"rival_theory": "Dualism", "no_difference_penalty_score": 0.9}]},
    "ap1": {**common, "consciousness_minimal_properties_status": "CONSCIOUSNESS_MINIMAL_PROPERTIES_REGISTERED", "minimal_properties_registered": True, "minimal_properties": [{"name": "unity"}]},
    "ap3": {**common, "consciousness_rf_property_mapping_status": "CONSCIOUSNESS_RF_PROPERTY_MAPPING_COMPLETED", "property_mapping_completed": True},
    "ap10": {**common, "consciousness_as_rf_equivalence_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED", "axis_resolved": True},
}

r = MinimalPropertyDenialChecker().step(inputs=synthetic_inputs, persist=False)

assert r.get("minimal_property_denial_status") == "MINIMAL_PROPERTY_DENIAL_CHECKED"
assert r.get("denial_check_completed") is True
assert r.get("step") == "AQ5"
assert r.get("axis", "AQ") == "AQ"
assert len(r.get("recovered_minimal_properties", [])) >= 9
assert len(r.get("minimal_property_denials", [])) >= 7
m = r.get("denial_metrics", {})
assert m.get("ontological_proof_score") == 0.0
assert m.get("phenomenal_proof_score") == 0.0
assert m.get("consciousness_proof_score", 0.0) == 0.0
assert m.get("aq4_no_difference_dependency_score") == 1.0
for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven"]:
    assert r.get(k) is False
assert r.get("phenomenology_undetermined") is True
assert r.get("functional_conclusion_only") is True
assert r.get("next_recommended_module") == "anti_rf_countermodel_evaluator"
print("AQ5_FINAL_LOCK_OK")
