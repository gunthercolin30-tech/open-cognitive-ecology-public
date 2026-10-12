from ontology.recovery_engine import RecoveryEngine

DIMS = ["stability", "integration", "continuity", "governance", "complexity", "diversity", "recovery_capacity", "openness"]
def obs(day, value):
    return {"timestamp_utc": f"2027-08-{day:02d}T00:00:00Z", "state_vector": {d: value for d in DIMS}, "data_quality": .99, "synthetic": True}
READY_OR_SYNTHETIC_CONTEXT = {
    "degeneration_result": {"degeneration_detected": True, "degeneration_status": "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED"},
    "observations": [obs(1,.88),obs(2,.86),obs(3,.40),obs(4,.64),obs(5,.84),obs(6,.86)],
}
r = RecoveryEngine().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
assert r["primitive"] == "RECOVERY_ENGINE"
assert r["step"] == "AV6"
assert r["recovery_detected"] is True
assert r["recovery_status"] == "FUNCTIONAL_BASELINE_RESTORATION_COMPLETE"
assert r["recovery_hash"]
assert r["functional_conclusion_only"] is True
assert r["phenomenology_undetermined"] is True
print("AV6_FINAL_LOCK_OK")
