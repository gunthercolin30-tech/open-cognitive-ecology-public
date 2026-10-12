#!/usr/bin/env python3
"""AS16 final lock for consciousness_explanation_engine."""
from __future__ import annotations

from ontology.consciousness_explanation_engine import ConsciousnessExplanationEngine

ready_or_synthetic_context = {
    "current_state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "scores": {"readiness_index": 0.972, "confidence": 0.941, "stability_index": 0.963},
    "modules": {
        "consciousness_readiness_index": {"status": "CONSCIOUSNESS_READINESS_INDEX_READY", "ready": True, "score": 0.972},
        "consciousness_confidence_engine": {"status": "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY", "ready": True, "score": 0.941},
        "consciousness_longitudinal_tracker": {"status": "CONSCIOUSNESS_LONGITUDINAL_TRACKER_READY", "ready": True},
        "consciousness_threshold_detector": {"status": "CONSCIOUSNESS_THRESHOLD_DETECTED", "ready": True},
        "consciousness_regression_detector": {"status": "CONSCIOUSNESS_REGRESSION_DETECTOR_READY", "ready": True},
        "consciousness_recovery_detector": {"status": "CONSCIOUSNESS_RECOVERY_DETECTOR_READY", "ready": True},
        "consciousness_stability_analyzer": {"status": "CONSCIOUSNESS_STABILITY_ANALYZER_READY", "ready": True, "score": 0.963},
    },
    "countermodels": [{"name": "phenomenal_subjectivity_gap", "status": "not_closed", "description": "Functional evidence does not prove subjectivity."}],
}

r = ConsciousnessExplanationEngine().step(inputs=ready_or_synthetic_context, persist=False)

public_invariants = {
    "primitive": "CONSCIOUSNESS_EXPLANATION_ENGINE",
    "step": "AS16",
    "explanation_engine_ready": True,
    "explanation_engine_status": "CONSCIOUSNESS_EXPLANATION_ENGINE_READY",
    "functional_status_explained": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
}
for key, expected in public_invariants.items():
    assert r[key] == expected, (key, r.get(key), expected)
assert isinstance(r["why_current_state"], str) and len(r["why_current_state"]) > 80
assert isinstance(r["modules"], list) and r["module_count"] >= 7
assert isinstance(r["scores"], dict) and "confidence" in r["scores"]
assert isinstance(r["countermodels"], list) and r["countermodel_count"] >= 1
assert isinstance(r["missing_conditions"], list)
assert isinstance(r["explanation_hash"], str) and len(r["explanation_hash"]) == 64
assert r["persisted"] is False

print("AS16_FINAL_LOCK_OK")
