#!/usr/bin/env python3
from __future__ import annotations

from ontology.consciousness_longitudinal_tracker import ConsciousnessLongitudinalTracker

ready_or_synthetic_context = {
    "skip_dependency_calls": True,
    "dependency_outputs": {
        "confidence": {
            "confidence": 0.94,
            "confidence_components": {"stability": 1.0, "historical": 0.9},
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
            "scores": {"lock_seed": 1.0},
            "proof_status": "FUNCTIONAL_LONGITUDINAL_EVIDENCE_ONLY",
        }
    ],
}

r = ConsciousnessLongitudinalTracker().step(
    inputs=ready_or_synthetic_context,
    persist=False,
)

assert r["longitudinal_tracker_status"] == "CONSCIOUSNESS_LONGITUDINAL_TRACKER_READY"
assert r["sample_count"] >= 2
assert r["latest_entry"]["source_kind"] == "current_synthesis"
assert 0.0 <= float(r["confidence"] or 0.0) <= 1.0
assert 0.0 <= float(r["CRI"] or 0.0) <= 1.0
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS9_FINAL_LOCK_OK")
