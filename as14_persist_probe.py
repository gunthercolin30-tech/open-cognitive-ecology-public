from pathlib import Path
from ontology.consciousness_recovery_detector import ConsciousnessRecoveryDetector

r = ConsciousnessRecoveryDetector().step(
    inputs={
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
    },
    persist=True,
)

assert r["persisted"] is True
assert r["output_path"]
assert Path(r["output_path"]).exists()
assert r["recovery_detector_ready"] is True
assert r["recovery_detected"] is True
assert r["recovery_event_type"] == "CONSCIOUSNESS_STATUS_RECOVERED"

print("AS14_PERSISTENCE_OK")
print(r["output_path"])
