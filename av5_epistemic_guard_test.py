from ontology.degeneration_detector import DegenerationDetector


def observation(day, value):
    return {
        "timestamp_utc": f"2027-03-{day:02d}T00:00:00Z",
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
            observation(1, 0.88),
            observation(2, 0.84),
            observation(3, 0.72),
            observation(4, 0.60),
            observation(5, 0.48),
        ],
    },
    persist=False,
)

assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True

print("AV5_EPISTEMIC_GUARD_OK")
