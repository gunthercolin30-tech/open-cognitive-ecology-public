#!/usr/bin/env python3
from copy import deepcopy
from ontology.developmental_dashboard import DevelopmentalDashboard

engine = DevelopmentalDashboard()
source = {
    "developmental_stage_classifier": {
        "classifier_status": "DEVELOPMENTAL_STAGE_CLASSIFIER_READY",
        "developmental_stage": "SPECIALIZATION",
        "stage_confidence": 0.88,
        "evidence_quality_score": 0.91,
        "stage_history": [
            {"developmental_stage": "MATURATION", "timestamp_utc": "2026-01-01T00:00:00Z"},
            {"developmental_stage": "SPECIALIZATION", "timestamp_utc": "2026-02-01T00:00:00Z"},
        ],
    },
    "developmental_prediction_engine": {
        "prediction_status": "DEVELOPMENTAL_PREDICTION_READY",
        "predicted_stage": "STABLE_DEVELOPED_REGIME",
        "prediction_confidence": 0.79,
        "prediction_uncertainty": 0.21,
        "input_quality_score": 0.90,
        "forecast_horizon": {"label": "MEDIUM", "windows": 3},
        "alternative_scenarios": [
            {"rank": 1, "stage": "STABLE_DEVELOPED_REGIME", "probability": 0.61},
            {"rank": 2, "stage": "BIFURCATION", "probability": 0.24},
        ],
    },
}
snapshot = deepcopy(source)
a = engine.step(inputs=source, persist=False)
b = engine.step(inputs=deepcopy(source), persist=False)

assert source == snapshot
assert a["dashboard_hash"] == b["dashboard_hash"]
assert a["exports"] == b["exports"]
assert a["export_integrity"] == b["export_integrity"]

changed = deepcopy(source)
changed["developmental_prediction_engine"]["predicted_stage"] = "BIFURCATION"
c = engine.step(inputs=changed, persist=False)
assert c["dashboard_hash"] != a["dashboard_hash"]
assert c["exports"] != a["exports"]

assert a["audit_trace"]["upstream_recalculation_performed"] is False
print("AV9_NON_REGRESSION_AND_DETERMINISM_OK")
