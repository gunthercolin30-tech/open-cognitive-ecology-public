#!/usr/bin/env python3
"""AS13 final lock for consciousness_regression_detector."""
from ontology.consciousness_regression_detector import ConsciousnessRegressionDetector

ready_or_synthetic_context = {
    "timeline": [
        {
            "timestamp_utc": "2026-07-08T10:00:00Z",
            "CRI": 0.97,
            "confidence": 0.94,
            "state": "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
        },
        {
            "timestamp_utc": "2026-07-08T11:00:00Z",
            "CRI": 0.90,
            "confidence": 0.87,
            "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
            "proof_status": "REGRESSED_BELOW_CONFIDENCE_MARGIN",
            "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
        },
    ],
}

r = ConsciousnessRegressionDetector().step(inputs=ready_or_synthetic_context, persist=False)

public_invariants = {
    "primitive": "CONSCIOUSNESS_REGRESSION_DETECTOR",
    "step": "AS13",
    "regression_detector_ready": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
}

for key, expected in public_invariants.items():
    assert r[key] == expected, (key, r.get(key), expected)

assert isinstance(r["regression_detected"], bool)
assert isinstance(r["regression_events"], list)
assert isinstance(r["regression_metrics"], dict)
assert 0 <= r["regression_metrics"].get("sample_count", 0)

print("AS13_FINAL_LOCK_OK")
