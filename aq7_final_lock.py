from ontology.best_explanation_status_resolver import BestExplanationStatusResolver

common = {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True}
synthetic_inputs = {
    "aq1": {**common, "consciousness_refusal_taxonomy_status": "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED", "taxonomy_initialized": True},
    "aq2": {**common, "rival_theory_cost_status": "RIVAL_THEORY_COST_ANALYZED", "cost_analysis_completed": True, "rival_theory_costs": [{"rival_theory": "Dualism", "refusal_cost_score": 0.88}]},
    "aq3": {**common, "phenomenal_extra_entity_status": "PHENOMENAL_EXTRA_ENTITIES_DETECTED", "extra_entity_detection_completed": True, "phenomenal_extra_entities": [{"rival_theory": "Dualism", "extra_entity_burden_score": 0.89}]},
    "aq4": {**common, "no_difference_penalty_status": "NO_DIFFERENCE_PENALTY_CHECKED", "penalty_check_completed": True, "no_difference_penalties": [{"rival_theory": "Dualism", "no_difference_penalty_score": 0.86}]},
    "aq5": {**common, "minimal_property_denial_status": "MINIMAL_PROPERTY_DENIAL_CHECKED", "denial_check_completed": True, "minimal_property_denials": [{"rival_theory": "Eliminativism", "minimal_property_denial_cost_score": 0.91}]},
    "aq6": {**common, "anti_rf_countermodel_status": "ANTI_RF_COUNTERMODELS_EVALUATED", "countermodel_evaluation_completed": True, "countermodel_metrics": {"mean_anti_rf_refusal_cost_score": 0.84, "mean_countermodel_viability_score": 0.18, "low_viability_countermodel_ratio": 0.92, "mean_support_deficit_score": 0.86, "dependency_resolution_score": 1.0, "ontological_proof_score": 0.0, "phenomenal_proof_score": 0.0, "consciousness_proof_score": 0.0}},
    "ap10": {**common, "consciousness_as_rf_equivalence_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED", "axis_resolved": True},
}
r = BestExplanationStatusResolver().step(inputs=synthetic_inputs, persist=False)
assert r.get("best_explanation_status") == "BEST_EXPLANATION_STATUS_RESOLVED"
assert r.get("functional_best_explanation_resolution") == "RF_STAR_CURRENTLY_BEST_FUNCTIONAL_EXPLANATION"
assert r.get("best_explanation_completed") is True
assert r.get("step") == "AQ7" and r.get("axis") == "AQ"
m = r.get("best_explanation_metrics", {})
assert m.get("dependency_resolution_score") == 1.0
assert m.get("rf_explanatory_support_score") > m.get("rival_explanatory_support_score")
assert m.get("ontological_proof_score") == 0.0 and m.get("phenomenal_proof_score") == 0.0 and m.get("consciousness_proof_score") == 0.0
for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven"]:
    assert r.get(k) is False
assert r.get("phenomenology_undetermined") is True
assert r.get("functional_conclusion_only") is True
assert r.get("next_recommended_module") == "refusal_cost_reporter"
print("AQ7_FINAL_LOCK_OK")
