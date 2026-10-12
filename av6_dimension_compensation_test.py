from ontology.recovery_engine import RecoveryEngine


DIMENSIONS = (
    "stability",
    "integration",
    "continuity",
    "governance",
    "complexity",
    "diversity",
    "recovery_capacity",
    "openness",
)


def observation(day, values):
    assert set(values) == set(DIMENSIONS)

    return {
        "timestamp_utc": f"2027-10-{day:02d}T00:00:00Z",
        "state_vector": values,
        "data_quality": 0.98,
        "synthetic": True,
    }


baseline = {
    dimension: 0.88
    for dimension in DIMENSIONS
}

trough = {
    dimension: 0.40
    for dimension in DIMENSIONS
}

compensated_1 = {
    "stability": 0.80,
    "integration": 0.45,
    "continuity": 0.82,
    "governance": 0.46,
    "complexity": 0.81,
    "diversity": 0.47,
    "recovery_capacity": 0.83,
    "openness": 0.44,
}

compensated_2 = {
    "stability": 0.82,
    "integration": 0.46,
    "continuity": 0.83,
    "governance": 0.47,
    "complexity": 0.82,
    "diversity": 0.48,
    "recovery_capacity": 0.84,
    "openness": 0.45,
}

compensated_3 = {
    "stability": 0.83,
    "integration": 0.47,
    "continuity": 0.84,
    "governance": 0.48,
    "complexity": 0.83,
    "diversity": 0.49,
    "recovery_capacity": 0.85,
    "openness": 0.46,
}

inputs = {
    "degeneration_result": {
        "degeneration_detected": True,
        "degeneration_status":
            "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED",
    },
    "baseline": baseline,
    "observations": [
        observation(1, baseline),
        observation(2, trough),
        observation(3, compensated_1),
        observation(4, compensated_2),
        observation(5, compensated_3),
    ],
}

result = RecoveryEngine().step(
    inputs=inputs,
    persist=False,
)

assert result["baseline_restored"] is False
assert result["new_regime_reconstruction"] is False

assert set(result["unrestored_dimensions"]).issuperset({
    "integration",
    "governance",
    "diversity",
    "openness",
})

assert len(result["unrestored_dimensions"]) >= 4
assert len(result["restored_dimensions"]) < len(DIMENSIONS)

assert result["recovery_status"] not in {
    "FUNCTIONAL_BASELINE_RESTORATION_COMPLETE",
    "FUNCTIONAL_NEW_REGIME_RECONSTRUCTION_DETECTED",
}

# Une récupération partielle peut être admise, mais jamais une
# restauration complète obtenue par simple compensation de moyenne.
if result["recovery_detected"]:
    assert result["recovery_status"] in {
        "FUNCTIONAL_RECOVERY_EMERGING",
        "FUNCTIONAL_PARTIAL_RECOVERY_DETECTED",
    }

assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True

print("AV6_DIMENSION_COMPENSATION_GUARD_OK")
