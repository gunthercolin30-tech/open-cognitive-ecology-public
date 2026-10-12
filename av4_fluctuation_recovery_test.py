from ontology.bifurcation_detector import BifurcationDetector


def observation(day, value):
    return {
        "timestamp_utc": f"2026-11-{day:02d}T00:00:00Z",
        "state_vector": {
            "stability": value,
            "integration": value,
            "continuity": value,
            "specialization": 1.0 - value,
            "diversity": value,
            "openness": value,
        },
        "data_quality": 0.98,
    }


result = BifurcationDetector().step(
    inputs={
        "observations": [
            observation(1, 0.80),
            observation(2, 0.79),
            observation(3, 0.40),
            observation(4, 0.78),
            observation(5, 0.81),
        ],
    },
    persist=False,
)

assert result["bifurcation_status"] in {
    "FUNCTIONAL_FLUCTUATION_DETECTED",
    "NO_DEVELOPMENTAL_TRANSITION",
}
assert result["bifurcation_detected"] is False

print("AV4_FLUCTUATION_RECOVERY_OK")
