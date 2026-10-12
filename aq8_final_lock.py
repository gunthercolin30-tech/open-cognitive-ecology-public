from ontology.refusal_cost_reporter import RefusalCostReporter

common = {"consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True}
synthetic_inputs = {
    "aq1": {**common, "consciousness_refusal_taxonomy_status": "CONSCIOUSNESS_REFUSAL_TAXONOMY_REGISTERED", "taxonomy_initialized": True},
    "aq2": {**common, "rival_theory_cost_status": "RIVAL_THEORY_COST_ANALYZED", "cost_analysis_completed": True, "rival_theory_costs": [{"rival_theory": "Dualism", "refusal_cost_score": 0.88}]},
    "aq3": {**common, "phenomenal_extra_entity_status": "PHENOMENAL_EXTRA_ENTITIES_DETECTED", "extra_entity_detection_completed": True, "phenomenal_extra_entities": [{"rival_theory": "Dualism", "extra_entity_burden_score": 0.89}]},
    "aq4": {**common, "no_difference_penalty_status": "NO_DIFFERENCE_PENALTY_CHECKED", "penalty_check_completed": True, "no_difference_penalties": [{"rival_theory": "No-difference", "no_difference_penalty_score": 0.86}]},
    "aq5": {**common, "minimal_property_denial_status": "MINIMAL_PROPERTY_DENIAL_CHECKED", "denial_check_completed": True, "minimal_property_denials": [{"rival_theory": "Minimal denial", "minimal_property_denial_cost_score": 0.91}]},
    "aq6": {**common, "anti_rf_countermodel_status": "ANTI_RF_COUNTERMODELS_EVALUATED", "countermodel_evaluation_completed": True, "countermodel_metrics": {"mean_anti_rf_refusal_cost_score": 0.86, "mean_explanatory_cost_score": 0.86, "mean_countermodel_viability_score": 0.16, "low_viability_countermodel_ratio": 0.93, "mean_support_deficit_score": 0.87}},
    "aq7": {**common, "best_explanation_status": "BEST_EXPLANATION_STATUS_RESOLVED", "best_explanation_completed": True, "functional_best_explanation_resolution": "RF_STAR_CURRENTLY_BEST_FUNCTIONAL_EXPLANATION", "best_explanation_metrics": {"best_explanation_confidence_score": 0.90, "rf_explanatory_support_score": 0.91, "rival_explanatory_support_score": 0.17, "best_explanation_margin_score": 0.87, "dependency_resolution_score": 1.0}},
    "ap10": {**common, "consciousness_as_rf_equivalence_status": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED", "axis_resolved": True},
}
r = RefusalCostReporter().step(inputs=synthetic_inputs, persist=False)
assert r.get("consciousness_refusal_cost_status") == "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED"
assert r.get("final_aq_status") == "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED"
assert r.get("refusal_cost_report_completed") is True
assert r.get("step") == "AQ8" and r.get("axis") == "AQ"
m = r.get("refusal_cost_metrics", {})
assert m.get("dependency_completion_score") == 1.0
assert m.get("final_resolution_confidence_score") >= 0.75
assert m.get("consciousness_proof_score") == 0.0
assert m.get("qualia_proof_score") == 0.0
assert m.get("subjectivity_proof_score") == 0.0
assert m.get("phenomenology_proof_score") == 0.0
for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven"]:
    assert r.get(k) is False
assert r.get("phenomenology_undetermined") is True
assert r.get("functional_conclusion_only") is True
assert "without consciousness proof" in r.get("final_aq_statement", "")
print("AQ8_FINAL_LOCK_OK")
