from ontology.degeneration_detector import DegenerationDetector


def observation(day, value):
    return {
        "timestamp_utc": f"2027-05-{day:02d}T00:00:00Z",
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
        "data_quality": 0.99,
    }


result = DegenerationDetector().step(
    inputs={
        "observations": [
            observation(1, 0.90),
            observation(2, 0.88),
            observation(3, 0.60),
            observation(4, 0.35),
            observation(5, 0.15),
        ],
    },
    persist=False,
)

assert result["degeneration_detected"] is True
assert result["severity"] in {"SEVERE", "COLLAPSE"}
assert result["degeneration_status"] in {
    "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED",
    "FUNCTIONAL_COLLAPSE_DETECTED",
}

print("AV5_COLLAPSE_OK")
