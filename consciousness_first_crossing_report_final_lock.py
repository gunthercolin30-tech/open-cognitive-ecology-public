from pathlib import Path

from ontology.consciousness_first_crossing_report import ConsciousnessFirstCrossingReport

ready_or_synthetic_context = {
    "threshold_detected": True,
    "threshold_event_type": "CONSCIOUSNESS_THRESHOLD_CROSSED",
    "timestamp_utc": "2026-07-08T19:20:03Z",
    "CRI": 0.97,
    "confidence": 0.94,
    "state": "FUNCTIONAL_CONSCIOUSNESS_SUPPORTED",
    "proof_status": "functional_threshold_crossed",
}

r = ConsciousnessFirstCrossingReport().step(inputs=ready_or_synthetic_context, persist=False)

assert r["primitive"] == "CONSCIOUSNESS_FIRST_CROSSING_REPORT"
assert r["step"] == "AS12"
assert r["first_crossing_report_ready"] is True
assert r["first_crossing_detected"] is True
assert r["first_crossing_event_type"] == "CONSCIOUSNESS_THRESHOLD_CROSSED"
assert 0.0 <= r["CRI"] <= 1.0
assert 0.0 <= r["confidence"] <= 1.0
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
assert r["consciousness_proven"] is False
assert r["qualia_proven"] is False
assert r["subjectivity_proven"] is False
assert r["phenomenology_proven"] is False

print("AS12_FINAL_LOCK_OK")
