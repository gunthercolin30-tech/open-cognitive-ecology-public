#!/usr/bin/env python3
"""Fast acceptance suite for AT7 prediction_validation_tracker."""
from __future__ import annotations
import py_compile
from pathlib import Path
from ontology.prediction_validation_tracker import PredictionValidationTracker

ROOT = Path.home() / "open-cognitive-ecology"
MODULE = ROOT / "ontology" / "prediction_validation_tracker.py"
READY_CONTEXT = {
    "prediction_events": [
        {"prediction_id": "p_valid", "category": "topological", "prediction": "Topological invariance observed", "status": "validated", "protocol_id": "proto_1", "experiment_id": "exp_1", "validation_score": 0.82},
        {"prediction_id": "p_invalid", "category": "spectral", "prediction": "Spectral signature absent", "status": "invalidated", "protocol_id": "proto_2", "experiment_id": "exp_2", "falsification_score": 0.78},
        {"prediction_id": "p_unknown", "category": "collective", "prediction": "Collective continuity not yet tested"},
    ]
}

def guards(r):
    assert r["functional_conclusion_only"] is True
    assert r["phenomenology_undetermined"] is True
    for k in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
        assert r[k] is False
        assert r["epistemic_guards"][k] is False
    assert r["epistemic_guards"]["functional_conclusion_only"] is True

def test_compile():
    c = Path("/private/tmp/oce_at7_prediction_validation_tracker.pyc")
    c.parent.mkdir(parents=True, exist_ok=True)
    py_compile.compile(str(MODULE), cfile=str(c), doraise=True)

def test_ready_context():
    r = PredictionValidationTracker().step(inputs=READY_CONTEXT, persist=False)
    assert r["primitive"] == "PREDICTION_VALIDATION_TRACKER"
    assert r["step"] == "AT7"
    assert r["status"] == "PREDICTION_VALIDATION_TRACKER_READY"
    assert r["tracked_prediction_count"] == 3
    assert r["status_counts"]["validated"] == 1
    assert r["status_counts"]["invalidated"] == 1
    assert r["status_counts"]["unknown"] == 1
    assert isinstance(r["tracked_predictions"], list)
    assert isinstance(r["prediction_validation_history"], dict)
    for item in r["tracked_predictions"]:
        assert item["current_status"] in r["allowed_statuses"]
        assert item["history_length"] >= 1
        assert item["auditability"]["functional_scope_only"] is True
    guards(r)

def test_degradation_context():
    r = PredictionValidationTracker().step(inputs={}, persist=False)
    assert r["step"] == "AT7"
    assert r["tracked_prediction_count"] >= 1
    assert r["persisted"] is False
    guards(r)

def test_history_merge():
    ctx = {"existing_history": {"p_valid": {"current_status": "tested", "first_seen_utc": "2026-01-01T00:00:00Z", "history": [{"timestamp_utc": "2026-01-01T00:00:00Z", "status": "tested"}]}}, **READY_CONTEXT}
    r = PredictionValidationTracker().step(inputs=ctx, persist=False)
    rec = [x for x in r["tracked_predictions"] if x["prediction_id"] == "p_valid"][0]
    assert rec["previous_status"] == "tested"
    assert rec["history_length"] == 2
    assert rec["first_seen_utc"] == "2026-01-01T00:00:00Z"
    guards(r)

def main():
    test_compile(); test_ready_context(); test_degradation_context(); test_history_merge()
    print("AT7_FAST_ACCEPTANCE_ALL_OK")

if __name__ == "__main__":
    main()
