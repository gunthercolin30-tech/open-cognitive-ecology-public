#!/usr/bin/env python3
"""Codex-compliant final lock for AT7."""
from __future__ import annotations
from ontology.prediction_validation_tracker import PredictionValidationTracker

READY_OR_SYNTHETIC_CONTEXT = {
    "prediction_events": [
        {"prediction_id": "lock_prediction", "category": "structural", "prediction": "Lock validation tracking event", "status": "tested", "protocol_id": "lock_protocol", "experiment_id": "lock_experiment", "validation_score": 0.55}
    ]
}

def main():
    r = PredictionValidationTracker().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert r["primitive"] == "PREDICTION_VALIDATION_TRACKER"
    assert r["step"] == "AT7"
    assert r["status"] == "PREDICTION_VALIDATION_TRACKER_READY"
    assert r["tracked_prediction_count"] >= 1
    assert isinstance(r["tracked_predictions"], list)
    assert isinstance(r["prediction_validation_history"], dict)
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
        assert r[k] is False
    print("AT7_FINAL_LOCK_OK")

if __name__ == "__main__":
    main()
