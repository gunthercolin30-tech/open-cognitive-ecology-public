from ontology.recovery_engine import RecoveryEngine


def observation(timestamp, value):
    return {
        "timestamp_utc": timestamp,
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
        "observations": [
            observation("2027-08-03T00:00:00Z", 0.45),
            observation("2027-08-01T00:00:00Z", 0.85),
            observation("2027-08-02T00:00:00Z", 0.65),
        ],
    },
    persist=False,
)

assert result["recovery_detected"] is False
assert result["recovery_status"] not in {
    "FUNCTIONAL_BASELINE_RESTORATION_COMPLETE",
    "FUNCTIONAL_NEW_REGIME_RECONSTRUCTION_DETECTED",
}

print("AV6_TEMPORAL_ORDER_DEGRADATION_OK")
