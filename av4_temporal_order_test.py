from ontology.bifurcation_detector import BifurcationDetector


def observation(timestamp, value):
    return {
        "timestamp_utc": timestamp,
        "state_vector": {
            "stability": value,
            "integration": value,
            "continuity": value,
            "specialization": 1.0 - value,
            "diversity": value,
            "openness": value,
        },
        "data_quality": 0.97,
    }


result = BifurcationDetector().step(
    inputs={
        "observations": [
            observation("2026-10-03T00:00:00Z", 0.40),
            observation("2026-10-01T00:00:00Z", 0.80),
            observation("2026-10-02T00:00:00Z", 0.75),
        ],
    },
    persist=False,
)

assert result["bifurcation_detected"] is False
assert result["bifurcation_status"] not in {
    "FUNCTIONAL_BIFURCATION_DETECTED",
    "FUNCTIONAL_MULTIPLE_BIFURCATIONS_DETECTED",
}

print("AV4_TEMPORAL_ORDER_DEGRADATION_OK")
