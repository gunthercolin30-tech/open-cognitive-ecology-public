from ontology.maturation_tracker import MaturationTracker


def observation(timestamp, value):
    return {
        "timestamp_utc": timestamp,
        "stability": value,
        "integration": value,
        "continuity": value,
        "governance": value,
        "complexity": value,
        "diversity": value,
        "recovery": value,
        "data_quality": 0.97,
        "synthetic": True,
    }


inputs = {
    "genesis_result": {
        "genesis_detected": True,
        "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
    },
    "observations": [
        observation("2026-05-03T00:00:00Z", 0.80),
        observation("2026-05-01T00:00:00Z", 0.50),
        observation("2026-05-02T00:00:00Z", 0.70),
    ],
}

result = MaturationTracker().step(
    inputs=inputs,
    persist=False,
)

assert result["maturation_complete"] is False
assert result["maturation_status"] != "FUNCTIONAL_MATURATION_COMPLETE"

print("AV2_TEMPORAL_ORDER_DEGRADATION_OK")
