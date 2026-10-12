from ontology.consciousness_longitudinal_tracker import ConsciousnessLongitudinalTracker

r = ConsciousnessLongitudinalTracker().step(
    inputs={},
    persist=False,
)

assert isinstance(r["timeline"], list)
assert len(r["timeline"]) == r["sample_count"]

if r["timeline"]:
    last = r["timeline"][-1]
    assert "confidence" in last
    assert "state" in last
    assert "timestamp_utc" in last

print("AS9_TIMELINE_CONSISTENCY_OK")
