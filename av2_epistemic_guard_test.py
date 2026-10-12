from ontology.maturation_tracker import MaturationTracker


def observation(day, value):
    return {
        "timestamp_utc": f"2026-05-{day:02d}T00:00:00Z",
        "stability": value,
        "integration": value,
        "continuity": value,
        "governance": value,
        "complexity": value,
        "diversity": value,
        "recovery": value,
        "data_quality": 0.98,
        "synthetic": True,
    }


inputs = {
    "genesis_result": {
        "genesis_detected": True,
        "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
    },
    "observations": [
        observation(1, 0.48),
        observation(2, 0.58),
        observation(3, 0.68),
        observation(4, 0.78),
        observation(5, 0.88),
    ],
}

result = MaturationTracker().step(
    inputs=inputs,
    persist=False,
)

assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True

print("AV2_EPISTEMIC_GUARD_OK")
