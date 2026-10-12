from ontology.recovery_engine import RecoveryEngine


def observation(day, value):
    return {
        "timestamp_utc": f"2027-10-{day:02d}T00:00:00Z",
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
            observation(3, 0.40),
            observation(4, 0.76),
            observation(5, 0.48),
            observation(6, 0.45),
        ],
    },
    persist=False,
)

assert result["recovery_detected"] is False
assert result["recovery_status"] in {
    "FUNCTIONAL_RECOVERY_TRANSIENT",
    "FUNCTIONAL_RECOVERY_NOT_DETECTED",
}

print("AV6_TRANSIENT_REBOUND_OK")
