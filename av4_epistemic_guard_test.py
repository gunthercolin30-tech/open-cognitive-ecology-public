from ontology.bifurcation_detector import BifurcationDetector


def observation(day, values):
    return {
        "timestamp_utc": f"2026-10-{day:02d}T00:00:00Z",
        "state_vector": values,
        "data_quality": 0.98,
    }


inputs = {
    "observations": [
        observation(1, {
            "stability": 0.80,
            "integration": 0.78,
            "continuity": 0.82,
            "specialization": 0.35,
            "diversity": 0.78,
            "openness": 0.88,
        }),
        observation(2, {
            "stability": 0.79,
            "integration": 0.77,
            "continuity": 0.81,
            "specialization": 0.36,
            "diversity": 0.77,
            "openness": 0.87,
        }),
        observation(3, {
            "stability": 0.52,
            "integration": 0.48,
            "continuity": 0.55,
            "specialization": 0.82,
            "diversity": 0.35,
            "openness": 0.42,
        }),
        observation(4, {
            "stability": 0.54,
            "integration": 0.50,
            "continuity": 0.56,
            "specialization": 0.84,
            "diversity": 0.34,
            "openness": 0.40,
        }),
        observation(5, {
            "stability": 0.55,
            "integration": 0.51,
            "continuity": 0.57,
            "specialization": 0.85,
            "diversity": 0.33,
            "openness": 0.39,
        }),
    ],
}

result = BifurcationDetector().step(
    inputs=inputs,
    persist=False,
)

assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True

print("AV4_EPISTEMIC_GUARD_OK")
