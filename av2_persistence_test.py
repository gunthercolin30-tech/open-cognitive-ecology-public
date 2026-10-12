from pathlib import Path

from ontology.maturation_tracker import MaturationTracker


def observation(day, value):
    return {
        "timestamp_utc": f"2026-06-{day:02d}T00:00:00Z",
        "stability": value,
        "integration": value,
        "continuity": value,
        "governance": value,
        "complexity": value,
        "diversity": value,
        "recovery": value,
        "data_quality": 0.98,
        "synthetic": True,
    }


inputs = {
    "genesis_result": {
        "genesis_detected": True,
        "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
    },
    "observations": [
        observation(1, 0.48),
        observation(2, 0.58),
        observation(3, 0.68),
        observation(4, 0.78),
        observation(5, 0.88),
    ],
}

tracker = MaturationTracker()

first = tracker.step(
    inputs=inputs,
    persist=True,
)

second = tracker.step(
    inputs=inputs,
    persist=True,
)

assert first["maturation_hash"] == second["maturation_hash"]
assert first["maturation_status"] == second["maturation_status"]
assert first["maturation_score"] == second["maturation_score"]

path_value = (
    first.get("persistence_path")
    or first.get("output_path")
    or first.get("report_path")
)

if path_value:
    assert Path(path_value).exists()

print("AV2_PERSISTENCE_AND_REEXECUTION_OK")
