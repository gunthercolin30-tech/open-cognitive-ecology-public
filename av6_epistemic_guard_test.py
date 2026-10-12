from ontology.recovery_engine import RecoveryEngine


def observation(day, value):
    return {
        "timestamp_utc": f"2027-08-{day:02d}T00:00:00Z",
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
            "degeneration_status":
                "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED",
        },
        "baseline": observation(1, 0.86)["state_vector"],
        "observations": [
            observation(1, 0.86),
            observation(2, 0.82),
            observation(3, 0.45),
            observation(4, 0.65),
            observation(5, 0.84),
            observation(6, 0.86),
        ],
    },
    persist=False,
)

assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True

print("AV6_EPISTEMIC_GUARD_OK")
