from __future__ import annotations

from ontology.discriminative_prediction_engine import DiscriminativePredictionEngine

ready_or_synthetic_context = {
    "axis": "AT",
    "step": "AT3",
    "theorem_predictions": [
        {
            "id": "AT3-FINAL-LOCK-GOVERNANCE",
            "category": "collective",
            "claim": "RF* predicts governance continuity and revocation-path observables that rival theories do not centrally require.",
            "observable_family": ["governance_continuity", "revocation_path", "epistemic_guard_presence"],
            "specificity": 0.86,
            "falsifiability": 0.83,
            "discriminative_potential": 0.84,
        },
        {
            "id": "AT3-FINAL-LOCK-DYNAMIC",
            "category": "dynamic",
            "claim": "RF* predicts separable regression/recovery dynamics under longitudinal governance constraints.",
            "observable_family": ["regression_rate", "recovery_rate", "transition_stability"],
            "specificity": 0.80,
            "falsifiability": 0.85,
            "discriminative_potential": 0.82,
        },
    ],
}

r = DiscriminativePredictionEngine().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "DISCRIMINATIVE_PREDICTION_ENGINE"
assert r["step"] == "AT3"
assert r["status"] == "DISCRIMINATIVE_PREDICTIONS_READY"
assert r["prediction_count"] >= 2
assert r["discriminative_prediction_count"] >= 1
assert r["compared_theory_count"] == 5
assert r["metrics"]["theory_coverage_ratio"] == 1.0
assert r["discrimination_policy"]["phenomenological_upgrade_blocked"] is True
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AT3_FINAL_LOCK_OK")
