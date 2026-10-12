from ontology.consciousness_threshold_detector import ConsciousnessThresholdDetector

ready_or_synthetic_context = {
    "CRI": 0.97,
    "confidence": 0.94,
    "axis_validation": {"AP": True, "AQ": True, "AR": True, "AN": True, "AO": True, "AL": True},
    "revocation_required": False,
}

r = ConsciousnessThresholdDetector().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_THRESHOLD_DETECTOR"
assert r["step"] == "AS11"
assert r["threshold_detector_ready"] is True
assert r["threshold_detected"] is True
assert r["threshold_event_type"] == "CONSCIOUSNESS_THRESHOLD_CROSSED"
assert r["threshold_detection_status"] == "CONSCIOUSNESS_THRESHOLD_DETECTED"
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

degraded = dict(ready_or_synthetic_context)
degraded["confidence"] = 0.42
d = ConsciousnessThresholdDetector().step(inputs=degraded, persist=False)
assert d["threshold_detected"] is False
assert "confidence" in d["missing_conditions"]

print("AS11_FAST_ACCEPTANCE_ALL_OK")
