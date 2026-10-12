from ontology.recovery_engine import RecoveryEngine

DIMS = ["stability", "integration", "continuity", "governance", "complexity", "diversity", "recovery_capacity", "openness"]
def obs(day, value, quality=.98):
    return {"timestamp_utc": f"2027-09-{day:02d}T00:00:00Z", "state_vector": {d: value for d in DIMS}, "data_quality": quality, "synthetic": True}

empty = RecoveryEngine().step(inputs={}, persist=False)
assert empty["recovery_status"] == "FUNCTIONAL_RECOVERY_UNDETERMINED"

no_degeneration = RecoveryEngine().step(inputs={"observations":[obs(1,.8),obs(2,.8),obs(3,.8),obs(4,.8),obs(5,.8)]}, persist=False)
assert no_degeneration["recovery_detected"] is False

partial = RecoveryEngine().step(inputs={"degeneration_result":{"degeneration_detected":True}, "observations":[obs(1,.86),obs(2,.84),obs(3,.35),obs(4,.52),obs(5,.60),obs(6,.61)]}, persist=False)
assert partial["recovery_status"] in {"FUNCTIONAL_PARTIAL_RECOVERY_DETECTED", "FUNCTIONAL_NEW_REGIME_RECONSTRUCTION_DETECTED", "FUNCTIONAL_RECOVERY_EMERGING"}

transient = RecoveryEngine().step(inputs={"degeneration_result":{"degeneration_detected":True}, "observations":[obs(1,.86),obs(2,.84),obs(3,.35),obs(4,.75),obs(5,.50),obs(6,.46)]}, persist=False)
assert transient["recovery_detected"] is False
assert transient["recovery_status"] == "FUNCTIONAL_RECOVERY_TRANSIENT"

bad_order = RecoveryEngine().step(inputs={"observations":[obs(3,.4),obs(1,.8),obs(2,.6)]}, persist=False)
assert bad_order["recovery_detected"] is False
assert bad_order["recovery_status"] == "FUNCTIONAL_RECOVERY_UNDETERMINED"

low_quality = RecoveryEngine().step(inputs={"observations":[obs(1,.86,.2),obs(2,.84,.2),obs(3,.35,.2),obs(4,.65,.2),obs(5,.82,.2)]}, persist=False)
assert low_quality["recovery_status"] == "FUNCTIONAL_RECOVERY_UNDETERMINED"
print("AV6_DEGRADATION_OK")
