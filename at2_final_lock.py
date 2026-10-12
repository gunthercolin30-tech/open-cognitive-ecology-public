from __future__ import annotations

from ontology.theorem_prediction_generator import TheoremPredictionGenerator

ready_or_synthetic_context = {
    "axis": "AT",
    "step": "AT2",
    "synthetic_context": True,
    "theorems": [
        {"theorem_id": "AT2-FINAL-LOCK-STRUCTURAL", "name": "final lock structural theorem", "statement": "If RF* theorem structure is adequate, observable dependency coverage and epistemic guard signatures must be present.", "source": "AT2_final_lock", "epistemic_status": "certified_functional"},
        {"theorem_id": "AT2-FINAL-LOCK-TOPOLOGICAL", "name": "final lock topological theorem", "statement": "If RF* reference-frame topology is adequate, frame-preservation observables must be generated.", "source": "AT2_final_lock", "epistemic_status": "certified_functional"},
    ],
}

r = TheoremPredictionGenerator().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "THEOREM_PREDICTION_GENERATOR"
assert r["step"] == "AT2"
assert r["status"] == "THEOREM_PREDICTION_GENERATOR_READY"
assert r["theorem_count"] >= 2
assert r["prediction_count"] >= 2
assert r["metrics"]["observable_completion_ratio"] == 1.0
assert all(p.get("observable_family") for p in r["theorem_predictions"])
assert all(p.get("validation_condition") for p in r["theorem_predictions"])
assert all(p.get("refutation_condition") for p in r["theorem_predictions"])
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AT2_FINAL_LOCK_OK")
