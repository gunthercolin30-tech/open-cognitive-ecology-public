from pathlib import Path
from ontology.consciousness_regression_detector import ConsciousnessRegressionDetector

r = ConsciousnessRegressionDetector().step(
    inputs={
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
        ]
    },
    persist=True,
)

assert r["persisted"] is True
assert r["output_path"]
assert Path(r["output_path"]).exists()
assert r["regression_detector_ready"] is True
assert r["regression_detected"] is True
assert r["cri_regression_detected"] is True
assert r["confidence_regression_detected"] is True

print("AS13_PERSISTENCE_OK")
print(r["output_path"])
