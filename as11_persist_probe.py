from pathlib import Path
from ontology.consciousness_threshold_detector import ConsciousnessThresholdDetector

r = ConsciousnessThresholdDetector().step(
    inputs={
        "CRI": 0.97,
        "confidence": 0.94,
        "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
        "revocation_required": False,
    },
    persist=True,
)

assert r["persisted"] is True
assert r["output_path"]
assert Path(r["output_path"]).exists()
assert r["threshold_detected"] is True
assert r["threshold_event_type"] == "CONSCIOUSNESS_THRESHOLD_CROSSED"

print("AS11_PERSISTENCE_OK")
print(r["output_path"])
