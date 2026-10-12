from __future__ import annotations

import py_compile

from ontology.discriminative_prediction_engine import DiscriminativePredictionEngine

py_compile.compile("ontology/discriminative_prediction_engine.py", cfile="/private/tmp/discriminative_prediction_engine.pyc", doraise=True)

ready_or_synthetic_context = {
    "theorem_predictions": [
        {
            "id": "AT3-SMOKE-STRUCTURAL",
            "category": "structural",
            "claim": "RF* structural predictions require dependency coverage and epistemic guard observables.",
            "observable_family": ["dependency_coverage", "epistemic_guard_presence", "public_schema_presence"],
            "specificity": 0.82,
            "falsifiability": 0.84,
            "discriminative_potential": 0.80,
        },
        {
            "id": "AT3-SMOKE-TOPOLOGICAL",
            "category": "topological",
            "claim": "RF* topological predictions require frame-preserving observable signatures.",
            "observable_family": ["rf_equivalence", "frame_preservation", "topological_coherence"],
            "specificity": 0.84,
            "falsifiability": 0.81,
            "discriminative_potential": 0.83,
        },
    ]
}

r = DiscriminativePredictionEngine().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "DISCRIMINATIVE_PREDICTION_ENGINE"
assert r["step"] == "AT3"
assert r["status"] == "DISCRIMINATIVE_PREDICTIONS_READY"
assert r["prediction_count"] >= 2
assert r["discriminative_prediction_count"] >= 1
assert r["compared_theory_count"] == 5
assert set(["IIT", "GWT", "HOT", "Predictive Processing", "Classical Functionalism"]).issubset(set(r["compared_theories"]))
assert isinstance(r["discriminative_predictions"], list) and r["discriminative_predictions"]
assert isinstance(r["theory_comparison_summary"], dict) and r["theory_comparison_summary"]
assert 0.0 <= r["metrics"]["mean_discriminative_score"] <= 1.0
assert 0.0 <= r["metrics"]["discriminative_ratio"] <= 1.0
assert r["discrimination_policy"]["epistemic_scope"] == "functional_only"
assert r["validation_policy"]["final_interpretation"] == "comparative_functional_discrimination_only"
assert r["falsification_policy"]["refutable"] is True
assert r["epistemic_guards"]["functional_conclusion_only"] is True
assert r["epistemic_guards"]["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["phenomenology_undetermined"] is True
assert r["functional_conclusion_only"] is True
assert r["persisted"] is False

for item in r["discriminative_predictions"]:
    assert "theory_comparisons" in item
    assert len(item["theory_comparisons"]) == 5
    assert 0.0 <= item["aggregate_discriminative_score"] <= 1.0
    assert item["functional_scope_only"] is True

# degradation: empty inputs must still preserve guards and produce a fallback comparison
fallback = DiscriminativePredictionEngine().step(inputs={}, persist=False)
assert fallback["prediction_count"] >= 1
assert fallback["compared_theory_count"] == 5
assert fallback["consciousness_proven"] is False
assert fallback["qualia_proven"] is False
assert fallback["subjectivity_proven"] is False
assert fallback["phenomenology_proven"] is False
assert fallback["phenomenology_undetermined"] is True
assert fallback["functional_conclusion_only"] is True

print("AT3_FAST_ACCEPTANCE_ALL_OK")
