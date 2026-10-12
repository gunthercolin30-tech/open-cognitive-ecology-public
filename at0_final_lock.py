from __future__ import annotations

from ontology.predictive_blueprint import PredictiveBlueprint

ready_or_synthetic_context = {
    "axis": "AT",
    "step": "AT0",
    "rf_star_context_ready": True,
    "synthetic_context": True,
}

r = PredictiveBlueprint().step(inputs=ready_or_synthetic_context, persist=False)

assert r["status"] == "PREDICTIVE_BLUEPRINT_READY"
assert r["predictive_blueprint_status"] == "PREDICTIVE_BLUEPRINT_READY"
assert r["rf_star_predictive_program_ready"] is True
assert r["blueprint"]["prediction_definition"]["requires_observable"] is True
assert r["blueprint"]["prediction_definition"]["requires_refutation_path"] is True
assert r["blueprint"]["refutation_rules"]["refutable"] is True
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AT0_FINAL_LOCK_OK")
