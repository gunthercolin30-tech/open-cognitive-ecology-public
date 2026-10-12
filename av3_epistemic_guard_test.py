from ontology.specialization_engine import SpecializationEngine


inputs = {
    "maturation_result": {
        "maturation_complete": True,
        "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
    },
    "observations": [
        {
            "timestamp_utc": f"2026-08-{day:02d}T00:00:00Z",
            "functional_profile": {
                "reasoning": value,
                "memory": (1.0 - value) / 3.0,
                "governance": (1.0 - value) / 3.0,
                "exploration": (1.0 - value) / 3.0,
            },
            "diversity": 0.40,
            "resource_cost": 0.35,
            "reversibility": 0.78,
            "openness": 0.86,
            "data_quality": 0.98,
        }
        for day, value in enumerate(
            [0.72, 0.76, 0.80, 0.84],
            start=1,
        )
    ],
}

result = SpecializationEngine().step(
    inputs=inputs,
    persist=False,
)

assert result["consciousness_proven"] is False
assert result["qualia_proven"] is False
assert result["subjectivity_proven"] is False
assert result["phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True

print("AV3_EPISTEMIC_GUARD_OK")
