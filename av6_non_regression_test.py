from ontology.recovery_engine import RecoveryEngine

DIMS = ["stability", "integration", "continuity", "governance", "complexity", "diversity", "recovery_capacity", "openness"]
def obs(day, value):
    return {"timestamp_utc": f"2027-10-{day:02d}T00:00:00Z", "state_vector": {d: value for d in DIMS}, "data_quality": .98, "synthetic": True}
inputs = {"degeneration_result":{"degeneration_detected":True}, "observations":[obs(1,.86),obs(2,.84),obs(3,.38),obs(4,.62),obs(5,.82),obs(6,.84)]}
a = RecoveryEngine().step(inputs=inputs, persist=False)
b = RecoveryEngine().step(inputs=inputs, persist=False)
assert a["recovery_hash"] == b["recovery_hash"]
assert a["recovery_score"] == b["recovery_score"]
assert a["baseline_restoration"] == b["baseline_restoration"]
assert a["new_regime_reconstruction"] == b["new_regime_reconstruction"]
changed = {"degeneration_result":{"degeneration_detected":True}, "observations":[obs(1,.86),obs(2,.84),obs(3,.38),obs(4,.62),obs(5,.70),obs(6,.72)]}
c = RecoveryEngine().step(inputs=changed, persist=False)
assert c["recovery_hash"] != a["recovery_hash"]
for key in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
    assert a[key] is False
print("AV6_NON_REGRESSION_AND_DETERMINISM_OK")
