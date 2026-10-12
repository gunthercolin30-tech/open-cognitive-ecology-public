from ontology.genesis_detector import GenesisDetector


def observation(timestamp, score):
    return {
        "timestamp_utc": timestamp,
        "rf_star_score": score,
        "stability": 0.95,
        "continuity": 0.95,
        "coherence": 0.95,
        "data_quality": 0.99,
        "synthetic": True,
    }


inputs = {
    "observations": [
        observation("2026-01-01T00:00:00Z", 0.20),
        observation("2026-01-02T00:00:00Z", 0.25),
        observation("2026-01-03T00:00:00Z", 0.90),
        observation("2026-01-04T00:00:00Z", 0.92),
        observation("2026-01-05T00:00:00Z", 0.94),
    ],
    "baseline": [
        observation("2026-01-01T00:00:00Z", 0.20),
        observation("2026-01-02T00:00:00Z", 0.25),
    ],
}

result = GenesisDetector().step(
    inputs=inputs,
    persist=False,
)

assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True

print("AV1_EPISTEMIC_GUARD_OK")
