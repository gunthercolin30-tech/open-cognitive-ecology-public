from pathlib import Path

from ontology.specialization_engine import SpecializationEngine


def observation(day, dominance):
    residual = (1.0 - dominance) / 3.0

    return {
        "timestamp_utc": f"2026-09-{day:02d}T00:00:00Z",
        "functional_profile": {
            "reasoning": dominance,
            "memory": residual,
            "governance": residual,
            "exploration": residual,
        },
        "diversity": 0.40,
        "resource_cost": 0.38,
        "reversibility": 0.76,
        "openness": 0.85,
        "data_quality": 0.98,
    }


inputs = {
    "maturation_result": {
        "maturation_complete": True,
        "maturation_status": "FUNCTIONAL_MATURATION_COMPLETE",
    },
    "observations": [
        observation(1, 0.74),
        observation(2, 0.78),
        observation(3, 0.82),
        observation(4, 0.84),
    ],
}

engine = SpecializationEngine()

first = engine.step(inputs=inputs, persist=True)
second = engine.step(inputs=inputs, persist=True)

assert first["specialization_hash"] == second["specialization_hash"]
assert first["specialization_status"] == second["specialization_status"]
assert first["specialization_strength"] == second[
    "specialization_strength"
]
assert first["closure_pressure"] == second["closure_pressure"]

path_value = (
    first.get("persistence_path")
    or first.get("output_path")
    or first.get("report_path")
)

if path_value:
    assert Path(path_value).exists()

print("AV3_PERSISTENCE_AND_REEXECUTION_OK")
