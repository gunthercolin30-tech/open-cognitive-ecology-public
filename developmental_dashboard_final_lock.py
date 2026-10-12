#!/usr/bin/env python3
from ontology.developmental_dashboard import DevelopmentalDashboard

READY_OR_SYNTHETIC_CONTEXT = {
    "developmental_stage_classifier": {
        "classifier_status": "DEVELOPMENTAL_STAGE_CLASSIFIER_READY",
        "developmental_stage": "MATURATION",
        "stage_confidence": 0.90,
        "evidence_quality_score": 0.92,
        "stage_history": [
            {"developmental_stage": "GENESIS", "timestamp_utc": "2026-01-01T00:00:00Z"},
            {"developmental_stage": "MATURATION", "timestamp_utc": "2026-02-01T00:00:00Z"},
        ],
    },
    "developmental_prediction_engine": {
        "prediction_status": "DEVELOPMENTAL_PREDICTION_READY",
        "predicted_stage": "SPECIALIZATION",
        "prediction_confidence": 0.80,
        "prediction_uncertainty": 0.20,
        "input_quality_score": 0.91,
        "forecast_horizon": {"label": "MEDIUM", "windows": 3},
        "alternative_scenarios": [
            {"rank": 1, "stage": "SPECIALIZATION", "probability": 0.60},
            {"rank": 2, "stage": "STABLE_DEVELOPED_REGIME", "probability": 0.25},
        ],
    },
}

r = DevelopmentalDashboard().step(
    inputs=READY_OR_SYNTHETIC_CONTEXT,
    persist=False,
)

assert r["primitive"] == "DEVELOPMENTAL_DASHBOARD"
assert r["step"] == "AV9"
assert r["dashboard_status"] == "DEVELOPMENTAL_DASHBOARD_READY"
assert len(r["dashboard_hash"]) == 64
assert set(r["exports"]) == {"json", "markdown", "html"}
assert r["exports"]["html"].startswith("<!doctype html>")
assert r["audit_trace"]["upstream_recalculation_performed"] is False
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True

print("AV9_FINAL_LOCK_OK")
