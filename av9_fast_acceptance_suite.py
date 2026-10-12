#!/usr/bin/env python3
from pathlib import Path
import json
import py_compile

from ontology.developmental_dashboard import DevelopmentalDashboard

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(
    str(ROOT / "ontology" / "developmental_dashboard.py"),
    cfile="/private/tmp/developmental_dashboard.pyc",
    doraise=True,
)

ready = {
    "developmental_blueprint": {"developmental_blueprint_status": "DEVELOPMENTAL_BLUEPRINT_READY"},
    "genesis_detector": {"genesis_detector_status": "GENESIS_DETECTOR_READY"},
    "maturation_tracker": {"maturation_tracker_status": "MATURATION_TRACKER_READY"},
    "specialization_engine": {"specialization_engine_status": "SPECIALIZATION_ENGINE_READY"},
    "bifurcation_detector": {"bifurcation_detector_status": "BIFURCATION_DETECTOR_READY"},
    "degeneration_detector": {"degeneration_detector_status": "DEGENERATION_DETECTOR_READY"},
    "recovery_engine": {"recovery_engine_status": "RECOVERY_ENGINE_READY"},
    "developmental_stage_classifier": {
        "classifier_status": "DEVELOPMENTAL_STAGE_CLASSIFIER_READY",
        "developmental_stage": "SPECIALIZATION",
        "stage_confidence": 0.91,
        "evidence_quality_score": 0.93,
        "stage_history": [
            {"developmental_stage": "GENESIS", "timestamp_utc": "2026-01-01T00:00:00Z"},
            {"developmental_stage": "MATURATION", "timestamp_utc": "2026-02-01T00:00:00Z"},
            {"developmental_stage": "SPECIALIZATION", "timestamp_utc": "2026-03-01T00:00:00Z"},
        ],
    },
    "developmental_prediction_engine": {
        "prediction_status": "DEVELOPMENTAL_PREDICTION_READY",
        "predicted_stage": "STABLE_DEVELOPED_REGIME",
        "prediction_confidence": 0.82,
        "prediction_uncertainty": 0.18,
        "input_quality_score": 0.92,
        "forecast_horizon": {"label": "MEDIUM", "windows": 3},
        "alternative_scenarios": [
            {"rank": 1, "stage": "STABLE_DEVELOPED_REGIME", "probability": 0.62},
            {"rank": 2, "stage": "BIFURCATION", "probability": 0.23},
        ],
    },
}

engine = DevelopmentalDashboard()
r = engine.step(inputs=ready, persist=False)

assert r["dashboard_status"] == "DEVELOPMENTAL_DASHBOARD_READY"
assert r["current_stage"] == "SPECIALIZATION"
assert r["predicted_stage"] == "STABLE_DEVELOPED_REGIME"
assert r["exports"]["html"].startswith("<!doctype html>")
assert "# AV9 Developmental Dashboard" in r["exports"]["markdown"]
assert json.loads(r["exports"]["json"])["dashboard_hash"] == r["dashboard_hash"]
assert r["audit_trace"]["upstream_recalculation_performed"] is False
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True

persisted = engine.step(inputs=ready, persist=True)
for key in ("json_path", "markdown_path", "html_path"):
    assert Path(persisted[key]).is_file()
assert persisted["persisted"] is True

print("AV9_FAST_ACCEPTANCE_OK")
