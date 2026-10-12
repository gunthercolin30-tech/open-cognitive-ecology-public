#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_longitudinal_tracker import ConsciousnessLongitudinalTracker

ready_or_synthetic_context = {
    "skip_dependency_calls": True,
    "dependency_outputs": {
        "confidence": {
            "confidence": 0.94,
            "confidence_components": {"stability": 1.0, "replications": 1.0},
            "confidence_metrics": {"confidence": 0.94},
            "confidence_status": "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY",
        },
        "readiness": {
            "cri": 0.93,
            "readiness_status": "CONSCIOUSNESS_READINESS_INDEX_READY",
        },
        "state_machine": {
            "current_state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
        },
    },
    "timeline": [
        {
            "date": "2026-07-08T14:37:00Z",
            "CRI": 0.93,
            "confidence": 0.94,
            "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
            "scores": {"seed": 1.0},
            "proof_status": "FUNCTIONAL_LONGITUDINAL_EVIDENCE_ONLY",
        }
    ],
}

r = ConsciousnessLongitudinalTracker().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_LONGITUDINAL_TRACKER"
assert r["step"] == "AS9"
assert r["longitudinal_tracker_ready"] is True
assert r["timeline_ready"] is True
assert r["time_series_ready"] is True
assert r["sample_count"] >= 2
assert isinstance(r["timeline"], list)
assert isinstance(r["time_series"], list)
assert isinstance(r["latest_entry"], dict)
assert "date" in r["latest_entry"]
assert "confidence" in r["latest_entry"]
assert "CRI" in r["latest_entry"]
assert "state" in r["latest_entry"]
assert "scores" in r["latest_entry"]
assert "proof_status" in r["latest_entry"]
assert isinstance(r["longitudinal_metrics"], dict)
assert r["longitudinal_metrics"]["sample_count"] == r["sample_count"]
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS9_FAST_ACCEPTANCE_ALL_OK")
