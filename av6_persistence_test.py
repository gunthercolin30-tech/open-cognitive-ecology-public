from pathlib import Path

from ontology.recovery_engine import RecoveryEngine


def observation(day, value):
    return {
        "timestamp_utc": f"2027-12-{day:02d}T00:00:00Z",
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


inputs = {
    "degeneration_result": {
        "degeneration_detected": True,
        "degeneration_status":
            "FUNCTIONAL_PROGRESSIVE_DEGENERATION_DETECTED",
    },
    "baseline": observation(1, 0.86)["state_vector"],
    "observations": [
        observation(1, 0.86),
        observation(2, 0.82),
        observation(3, 0.42),
        observation(4, 0.64),
        observation(5, 0.82),
        observation(6, 0.86),
    ],
}

engine = RecoveryEngine()

first = engine.step(inputs=inputs, persist=True)
second = engine.step(inputs=inputs, persist=True)

assert first["recovery_hash"] == second["recovery_hash"]
assert first["recovery_status"] == second["recovery_status"]
assert first["recovery_score"] == second["recovery_score"]
assert first["baseline_restoration"] == second[
    "baseline_restoration"
]

path_value = (
    first.get("persistence_path")
    or first.get("output_path")
    or first.get("report_path")
)

if path_value:
    assert Path(path_value).exists()

print("AV6_PERSISTENCE_AND_REEXECUTION_OK")
