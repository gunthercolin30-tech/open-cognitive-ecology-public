from ontology.recovery_engine import RecoveryEngine


def observation(day, values):
    return {
        "timestamp_utc": f"2027-11-{day:02d}T00:00:00Z",
        "state_vector": values,
        "data_quality": 0.99,
    }


baseline = {
    "stability": 0.86,
    "integration": 0.78,
    "continuity": 0.84,
    "governance": 0.72,
    "complexity": 0.68,
    "diversity": 0.82,
    "recovery_capacity": 0.76,
    "openness": 0.88,
}

new_regime = {
    "stability": 0.80,
    "integration": 0.90,
    "continuity": 0.78,
    "governance": 0.88,
    "complexity": 0.90,
    "diversity": 0.76,
    "recovery_capacity": 0.84,
    "openness": 0.92,
}

result = RecoveryEngine().step(
    inputs={
        "degeneration_result": {
            "degeneration_detected": True,
            "degeneration_status":
                "FUNCTIONAL_SEVERE_DEGENERATION_DETECTED",
        },
        "baseline": baseline,
        "bifurcation_result": {
            "bifurcation_detected": True,
            "bifurcation_status": "FUNCTIONAL_BIFURCATION_DETECTED",
        },
        "observations": [
            observation(1, baseline),
            observation(2, {
                key: 0.42 for key in baseline
            }),
            observation(3, {
                key: 0.55 for key in baseline
            }),
            observation(4, new_regime),
            observation(5, new_regime),
            observation(6, new_regime),
        ],
    },
    persist=False,
)

assert result["recovery_detected"] is True
assert result["new_regime_reconstruction"] is True
assert result["recovery_status"] == (
    "FUNCTIONAL_NEW_REGIME_RECONSTRUCTION_DETECTED"
)

print("AV6_NEW_REGIME_RECONSTRUCTION_OK")
