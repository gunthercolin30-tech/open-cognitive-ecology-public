from pathlib import Path
import py_compile

from ontology.recovery_engine import RecoveryEngine

ROOT = Path.home() / "open-cognitive-ecology"
py_compile.compile(str(ROOT / "ontology" / "recovery_engine.py"), cfile="/private/tmp/recovery_engine.pyc", doraise=True)

DIMS = ["stability", "integration", "continuity", "governance", "complexity", "diversity", "recovery_capacity", "openness"]

def obs(day, value, values=None):
    vector = {d: value for d in DIMS}
    if values:
        vector.update(values)
    return {"timestamp_utc": f"2027-08-{day:02d}T00:00:00Z", "state_vector": vector, "data_quality": 0.98, "synthetic": True}

complete = RecoveryEngine().step(inputs={
    "degeneration_result": {"degeneration_detected": True, "degeneration_status": "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED"},
    "observations": [obs(1, .86), obs(2, .84), obs(3, .42), obs(4, .68), obs(5, .83), obs(6, .85)],
}, persist=False)
assert complete["recovery_detected"] is True
assert complete["recovery_status"] == "FUNCTIONAL_BASELINE_RESTORATION_COMPLETE"
assert complete["baseline_restored"] is True
assert complete["recovery_score"] >= .80

new_regime = RecoveryEngine().step(inputs={
    "degeneration_result": {"degeneration_detected": True},
    "observations": [
        obs(1, .86), obs(2, .84), obs(3, .35),
        obs(4, .68, {"complexity": .78, "integration": .76}),
        obs(5, .70, {"complexity": .80, "integration": .78}),
        obs(6, .71, {"complexity": .81, "integration": .79}),
    ],
}, persist=False)
assert new_regime["recovery_detected"] is True
assert new_regime["recovery_status"] in {"FUNCTIONAL_NEW_REGIME_RECONSTRUCTION_DETECTED", "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED"}
assert new_regime["new_regime_viability"] >= .60

stable = RecoveryEngine().step(inputs={"observations": [obs(1,.8),obs(2,.8),obs(3,.8),obs(4,.8),obs(5,.8)]}, persist=False)
assert stable["recovery_detected"] is False

first = RecoveryEngine().step(inputs={"observations": [obs(1,.86),obs(2,.84),obs(3,.42),obs(4,.68),obs(5,.83),obs(6,.85)]}, persist=True)
second = RecoveryEngine().step(inputs={"observations": [obs(1,.86),obs(2,.84),obs(3,.42),obs(4,.68),obs(5,.83),obs(6,.85)]}, persist=False)
assert first["recovery_hash"] == second["recovery_hash"]
assert Path(first["persistence_path"]).exists()
for key in ["consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven"]:
    assert complete[key] is False
assert complete["functional_conclusion_only"] is True
assert complete["phenomenology_undetermined"] is True
print("AV6_FAST_ACCEPTANCE_OK")


# AV6_PARTIAL_RECOVERY_PERMANENT_LOCK
# A persistent recovery of roughly half the distance from the trough to the
# baseline is partial recovery, not a reconstructed regime without structural
# change evidence.
def _av6_partial_recovery_permanent_lock():
    from ontology.recovery_engine import RecoveryEngine

    def obs(day, value):
        return {
            "timestamp_utc": f"2027-09-{day:02d}T00:00:00Z",
            "state_vector": {
                "stability": value,
                "integration": value,
                "continuity": value,
                "governance": value,
                "complexity": value,
                "diversity": value,
                "recovery_capacity": value,
                "openness": value,
            },
            "data_quality": 0.98,
        }

    result = RecoveryEngine().step(
        inputs={
            "degeneration_result": {
                "degeneration_detected": True,
                "degeneration_status": "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED",
            },
            "baseline": obs(1, 0.88)["state_vector"],
            "observations": [
                obs(1, 0.88), obs(2, 0.82), obs(3, 0.42),
                obs(4, 0.55), obs(5, 0.65), obs(6, 0.68),
            ],
        },
        persist=False,
    )
    assert result["recovery_status"] == "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED"
    assert result["recovery_detected"] is True
    assert result["baseline_restored"] is False
    assert result["new_regime_reconstruction"] is False
    assert 0.50 <= result["baseline_restoration"] <= 0.60


_av6_partial_recovery_permanent_lock()
