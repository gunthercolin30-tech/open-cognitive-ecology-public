from ontology.degeneration_detector import DegenerationDetector


def observation(day, values):
    return {
        "timestamp_utc": f"2027-06-{day:02d}T00:00:00Z",
        "state_vector": values,
        "data_quality": 0.98,
    }


result = DegenerationDetector().step(
    inputs={
        "observations": [
            observation(1, {
                "stability": 0.76,
                "integration": 0.62,
                "continuity": 0.74,
                "governance": 0.65,
                "complexity": 0.58,
                "diversity": 0.78,
                "recovery_capacity": 0.72,
                "openness": 0.86,
            }),
            observation(2, {
                "stability": 0.75,
                "integration": 0.64,
                "continuity": 0.73,
                "governance": 0.67,
                "complexity": 0.60,
                "diversity": 0.79,
                "recovery_capacity": 0.73,
                "openness": 0.87,
            }),
            observation(3, {
                "stability": 0.70,
                "integration": 0.80,
                "continuity": 0.72,
                "governance": 0.78,
                "complexity": 0.82,
                "diversity": 0.76,
                "recovery_capacity": 0.74,
                "openness": 0.88,
            }),
            observation(4, {
                "stability": 0.71,
                "integration": 0.82,
                "continuity": 0.73,
                "governance": 0.80,
                "complexity": 0.84,
                "diversity": 0.77,
                "recovery_capacity": 0.75,
                "openness": 0.89,
            }),
        ],
        "bifurcation_result": {
            "bifurcation_detected": True,
            "bifurcation_status": "FUNCTIONAL_BIFURCATION_DETECTED",
        },
    },
    persist=False,
)

assert result["degeneration_detected"] is False

print("AV5_NON_DEGENERATIVE_BIFURCATION_OK")
