from ontology.degeneration_detector import DegenerationDetector


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


result = DegenerationDetector().step(
    inputs={
        "observations": [
            observation("2027-03-03T00:00:00Z", 0.55),
            observation("2027-03-01T00:00:00Z", 0.85),
            observation("2027-03-02T00:00:00Z", 0.72),
        ],
    },
    persist=False,
)

assert result["degeneration_detected"] is False
assert result["degeneration_status"] not in {
    "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED",
    "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED",
    "FUNCTIONAL_COLLAPSE_DETECTED",
}

print("AV5_TEMPORAL_ORDER_DEGRADATION_OK")
