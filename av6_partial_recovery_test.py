from ontology.recovery_engine import RecoveryEngine


def observation(day, value):
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
            "degeneration_status":
                "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED",
        },
        "baseline": observation(1, 0.88)["state_vector"],
        "observations": [
            observation(1, 0.88),
            observation(2, 0.82),
            observation(3, 0.42),
            observation(4, 0.55),
            observation(5, 0.65),
            observation(6, 0.68),
        ],
    },
    persist=False,
)

assert result["recovery_status"] in {
    "FUNCTIONAL_RECOVERY_EMERGING",
    "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED",
}
assert result["baseline_restored"] is False

print("AV6_PARTIAL_RECOVERY_OK")
