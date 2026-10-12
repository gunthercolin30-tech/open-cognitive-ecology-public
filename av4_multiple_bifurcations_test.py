from ontology.bifurcation_detector import BifurcationDetector


def observation(day, a, b, c):
    return {
        "timestamp_utc": f"2026-12-{day:02d}T00:00:00Z",
        "state_vector": {
            "stability": a,
            "integration": a,
            "continuity": a,
            "specialization": b,
            "diversity": c,
            "openness": c,
        },
        "data_quality": 0.99,
    }


inputs = {
    "observations": [
        observation(1, 0.82, 0.25, 0.82),
        observation(2, 0.81, 0.26, 0.81),
        observation(3, 0.52, 0.78, 0.42),
        observation(4, 0.51, 0.80, 0.40),
        observation(5, 0.83, 0.28, 0.84),
        observation(6, 0.84, 0.27, 0.85),
    ],
}

result = BifurcationDetector().step(
    inputs=inputs,
    persist=False,
)

assert result["bifurcation_count"] >= 2
assert result["multiple_bifurcations_detected"] is True
assert result["bifurcation_status"] == (
    "FUNCTIONAL_MULTIPLE_BIFURCATIONS_DETECTED"
)

print("AV4_MULTIPLE_BIFURCATIONS_OK")
