from __future__ import annotations

from ontology.prediction_registry import PredictionRegistry

ready_or_synthetic_context = {
    "axis": "AT",
    "step": "AT1",
    "predictive_blueprint_ready": True,
    "synthetic_context": True,
}

r = PredictionRegistry().step(inputs=ready_or_synthetic_context, persist=False)

assert r["status"] == "PREDICTION_REGISTRY_READY"
assert r["prediction_registry_status"] == "PREDICTION_REGISTRY_READY"
assert r["registry_ready"] is True
assert set(r["predictions_by_category"].keys()) >= {"structural", "dynamic", "topological", "spectral", "developmental", "collective"}
assert r["validation"]["registry_valid"] is True
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AT1_FINAL_LOCK_OK")
