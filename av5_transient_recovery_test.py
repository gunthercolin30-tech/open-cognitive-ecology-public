from ontology.degeneration_detector import DegenerationDetector


def observation(day, value):
    return {
        "timestamp_utc": f"2027-04-{day:02d}T00:00:00Z",
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
            observation(1, 0.84),
            observation(2, 0.82),
            observation(3, 0.52),
            observation(4, 0.80),
            observation(5, 0.85),
        ],
    },
    persist=False,
)

assert result["degeneration_detected"] is False
assert result["degeneration_status"] in {
    "FUNCTIONAL_TRANSIENT_DECLINE_RECOVERED",
    "FUNCTIONAL_DEGENERATION_NOT_DETECTED",
}

print("AV5_TRANSIENT_RECOVERY_OK")
