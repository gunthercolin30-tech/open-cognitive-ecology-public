#!/usr/bin/env python3
"""AS16 fast acceptance suite for consciousness_explanation_engine."""
from __future__ import annotations

import py_compile
from pathlib import Path

from ontology.consciousness_explanation_engine import ConsciousnessExplanationEngine

ROOT = Path.home() / "open-cognitive-ecology"
private_tmp = Path("/private/tmp")
private_tmp.mkdir(parents=True, exist_ok=True)
py_compile.compile(str(ROOT / "ontology" / "consciousness_explanation_engine.py"), cfile=str(private_tmp / "consciousness_explanation_engine.pyc"), doraise=True)

ready_or_synthetic_context = {
    "current_state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "scores": {
        "readiness_index": 0.972,
        "confidence": 0.941,
        "stability_index": 0.963,
        "regression_rate": 0.01,
        "recovery_rate": 0.02,
        "hazard_rate": 0.005,
    },
    "modules": {
        "consciousness_readiness_index": {"status": "CONSCIOUSNESS_READINESS_INDEX_READY", "ready": True, "score": 0.972},
        "consciousness_confidence_engine": {"status": "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY", "ready": True, "score": 0.941},
        "consciousness_longitudinal_tracker": {"status": "CONSCIOUSNESS_LONGITUDINAL_TRACKER_READY", "ready": True},
        "consciousness_threshold_detector": {"status": "CONSCIOUSNESS_THRESHOLD_DETECTED", "ready": True},
        "consciousness_regression_detector": {"status": "CONSCIOUSNESS_REGRESSION_DETECTOR_READY", "ready": True},
        "consciousness_recovery_detector": {"status": "CONSCIOUSNESS_RECOVERY_DETECTOR_READY", "ready": True},
        "consciousness_stability_analyzer": {"status": "CONSCIOUSNESS_STABILITY_ANALYZER_READY", "ready": True, "score": 0.963},
    },
    "countermodels": [
        {"name": "phenomenal_subjectivity_gap", "status": "not_closed", "description": "Functional records do not prove phenomenology."}
    ],
}

r = ConsciousnessExplanationEngine().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_EXPLANATION_ENGINE"
assert r["step"] == "AS16"
assert r["explanation_engine_ready"] is True
assert r["explanation_engine_status"] == "CONSCIOUSNESS_EXPLANATION_ENGINE_READY"
assert r["functional_status_explained"] is True
assert isinstance(r["why_current_state"], str) and "functional" in r["why_current_state"].lower()
assert isinstance(r["modules"], list) and len(r["modules"]) >= 7
assert r["available_module_count"] >= 7
assert isinstance(r["scores"], dict) and r["scores"]["confidence"] >= 0.9
assert isinstance(r["countermodels"], list) and r["countermodel_count"] >= 1
assert isinstance(r["missing_conditions"], list)
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False
assert r["persisted"] is False

empty = ConsciousnessExplanationEngine().step(inputs={}, persist=False)
assert empty["explanation_engine_ready"] is True
assert empty["current_state"] == "NOT_EVALUATED"
assert empty["functional_conclusion_only"] is True
assert empty["phenomenology_undetermined"] is True

low_confidence = ConsciousnessExplanationEngine().step(
    inputs={"scores": {"readiness_index": 0.8, "confidence": 0.7}, "modules": {}},
    persist=False,
)
assert any("Confidence below" in item for item in low_confidence["missing_conditions"])
assert any("Readiness" in item for item in low_confidence["missing_conditions"])

print("AS16_FAST_ACCEPTANCE_ALL_OK")
