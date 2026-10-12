from ontology.specialization_engine import SpecializationEngine


def observation(timestamp, dominance):
    residual = (1.0 - dominance) / 3.0

    return {
        "timestamp_utc": timestamp,
        "functional_profile": {
            "reasoning": dominance,
            "memory": residual,
            "governance": residual,
            "exploration": residual,
        },
        "diversity": 0.42,
        "resource_cost": 0.35,
        "reversibility": 0.80,
        "openness": 0.87,
        "data_quality": 0.98,
    }


result = SpecializationEngine().step(
    inputs={
        "maturation_result": {
            "maturation_complete": True,
            "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
        },
        "observations": [
            observation("2026-08-03T00:00:00Z", 0.82),
            observation("2026-08-01T00:00:00Z", 0.74),
            observation("2026-08-02T00:00:00Z", 0.78),
        ],
    },
    persist=False,
)

assert result["specialization_status"] not in {
    "FUNCTIONAL_SPECIALIZATION_STABLE",
    "FUNCTIONAL_SPECIALIZATION_STRONG",
}

print("AV3_TEMPORAL_ORDER_DEGRADATION_OK")
