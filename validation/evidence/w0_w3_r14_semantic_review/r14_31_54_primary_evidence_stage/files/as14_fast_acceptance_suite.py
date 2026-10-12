#!/usr/bin/env python3
"""AS14 fast acceptance suite for consciousness_recovery_detector."""
from ontology.consciousness_recovery_detector import ConsciousnessRecoveryDetector

ready_or_synthetic_context = {
    "timeline": [
        {
            "timestamp_utc": "2026-07-08T10:00:00Z",
            "CRI": 0.91,
            "confidence": 0.87,
            "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
            "proof_status": "REGRESSED_BELOW_CONFIDENCE_MARGIN",
            "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
        },
        {
            "timestamp_utc": "2026-07-08T11:00:00Z",
            "CRI": 0.97,
            "confidence": 0.94,
            "state": "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "proof_status": "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
        },
    ],
    "regression_detected": True,
    "revocation_required": False,
    "merge_persisted_timeline": False,
}

r = ConsciousnessRecoveryDetector().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_RECOVERY_DETECTOR"
assert r["step"] == "AS14"
assert r["public_schema_version"] == "1.0.0"
assert r["recovery_detector_ready"] is True
assert r["recovery_detected"] is True
assert r["recovery_event_type"] == "CONSCIOUSNESS_STATUS_RECOVERED"
assert isinstance(r["recovery_events"], list)
assert isinstance(r["recovery_metrics"], dict)
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

no_prior = ConsciousnessRecoveryDetector().step(
    inputs={"timeline": [ready_or_synthetic_context["timeline"][1]], "regression_detected": False, "merge_persisted_timeline": False},
    persist=False,
)
assert no_prior["recovery_detected"] is False
assert "No prior regression" in no_prior["failure_conditions"][0]

still_degraded = ConsciousnessRecoveryDetector().step(
    inputs={
        "timeline": [ready_or_synthetic_context["timeline"][0]],
        "regression_detected": True,
        "merge_persisted_timeline": False,
    },
    persist=False,
)
assert still_degraded["recovery_detected"] is False
assert "CRI" in still_degraded["missing_conditions"] or "confidence" in still_degraded["missing_conditions"]

print("AS14_FAST_ACCEPTANCE_ALL_OK")
