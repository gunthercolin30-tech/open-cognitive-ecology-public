from ontology.genesis_detector import GenesisDetector


inputs = {
    "observations": [
        {
            "timestamp_utc": "2026-01-03T00:00:00Z",
            "rf_star_score": 0.90,
            "stability": 0.90,
            "continuity": 0.90,
            "coherence": 0.90,
            "data_quality": 0.95,
            "synthetic": True,
        },
        {
            "timestamp_utc": "2026-01-01T00:00:00Z",
            "rf_star_score": 0.20,
            "stability": 0.90,
            "continuity": 0.90,
            "coherence": 0.90,
            "data_quality": 0.95,
            "synthetic": True,
        },
        {
            "timestamp_utc": "2026-01-02T00:00:00Z",
            "rf_star_score": 0.92,
            "stability": 0.90,
            "continuity": 0.90,
            "coherence": 0.90,
            "data_quality": 0.95,
            "synthetic": True,
        },
    ],
}

result = GenesisDetector().step(
    inputs=inputs,
    persist=False,
)

assert result["genesis_detected"] is False
assert result["genesis_status"] != "FUNCTIONAL_GENESIS_DETECTED"

print("AV1_TEMPORAL_ORDER_DEGRADATION_OK")
