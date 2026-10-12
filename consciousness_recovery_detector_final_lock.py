#!/usr/bin/env python3
"""AS14 final lock for consciousness_recovery_detector."""
from ontology.consciousness_recovery_detector import ConsciousnessRecoveryDetector

ready_or_synthetic_context = {
    "timeline": [
        {
            "timestamp_utc": "2026-07-08T10:00:00Z",
            "CRI": 0.90,
            "confidence": 0.86,
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

public_invariants = {
    "primitive": "CONSCIOUSNESS_RECOVERY_DETECTOR",
    "step": "AS14",
    "recovery_detector_ready": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
}

for key, expected in public_invariants.items():
    assert r[key] == expected, (key, r.get(key), expected)

assert r["recovery_detected"] is True
assert r["recovery_event_type"] == "CONSCIOUSNESS_STATUS_RECOVERED"
assert isinstance(r["recovery_events"], list)
assert isinstance(r["recovery_metrics"], dict)

print("AS14_FINAL_LOCK_OK")
