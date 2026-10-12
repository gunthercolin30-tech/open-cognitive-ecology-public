from ontology.predictive_theory_certifier import PredictiveTheoryCertifier

components = [
    "predictive_blueprint",
    "prediction_registry",
    "theorem_prediction_generator",
    "discriminative_prediction_engine",
    "measurable_signature_builder",
    "falsification_protocol_generator",
    "unexpected_prediction_detector",
    "prediction_validation_tracker",
    "predictive_power_index",
    "prediction_dashboard",
]

bad = {
    name: {
        "status": "FAILED",
        "complete": False,
        "ready": False,
        "validated": False,
        "predictive_power_index": 0.0,
        "prediction_count": 0,
        "signature_count": 0,
        "protocol_count": 0,
        "tracked_prediction_count": 0,
        "discriminative_prediction_count": 0,
        "unexpected_prediction_count": 0,
    }
    for name in components
}

r = PredictiveTheoryCertifier().step(inputs=bad, persist=False)

assert r["step"] == "AT10"
assert r["predictive_theory_certified"] is False
assert r["certification_status"] != "RF_PREDICTIVE_THEORY_CERTIFIED"
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AT10_DEGRADATION_FINAL_LOCK_OK")
