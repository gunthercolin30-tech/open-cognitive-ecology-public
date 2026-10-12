#!/usr/bin/env python3
"""AS13 fast acceptance suite for consciousness_regression_detector."""
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
            "CRI": 0.91,
            "confidence": 0.88,
            "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
            "proof_status": "REGRESSED_BELOW_CONFIDENCE_MARGIN",
            "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
        },
    ],
    "cri_drop_threshold": 0.03,
    "confidence_drop_threshold": 0.03,
    "merge_persisted_timeline": False,
}

r = ConsciousnessRegressionDetector().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_REGRESSION_DETECTOR"
assert r["step"] == "AS13"
assert r["public_schema_version"] == "1.0.0"
assert r["regression_detector_ready"] is True
assert r["regression_detected"] is True
assert r["cri_regression_detected"] is True
assert r["confidence_regression_detected"] is True
assert isinstance(r["regression_events"], list)
assert isinstance(r["regression_metrics"], dict)
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

stable = ConsciousnessRegressionDetector().step(inputs={"timeline": [ready_or_synthetic_context["timeline"][0]]}, persist=False)
assert stable["regression_detected"] is False
assert stable["regression_status"] == "NO_CONSCIOUSNESS_REGRESSION_DETECTED"

print("AS13_FAST_ACCEPTANCE_ALL_OK")
