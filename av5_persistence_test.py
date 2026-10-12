from pathlib import Path

from ontology.degeneration_detector import DegenerationDetector


def observation(day, value):
    return {
        "timestamp_utc": f"2027-07-{day:02d}T00:00:00Z",
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
    "observations": [
        observation(1, 0.88),
        observation(2, 0.84),
        observation(3, 0.72),
        observation(4, 0.60),
        observation(5, 0.48),
    ],
}

detector = DegenerationDetector()

first = detector.step(inputs=inputs, persist=True)
second = detector.step(inputs=inputs, persist=True)

assert first["degeneration_hash"] == second["degeneration_hash"]
assert first["degeneration_status"] == second["degeneration_status"]
assert first["degeneration_score"] == second["degeneration_score"]
assert first["severity"] == second["severity"]

path_value = (
    first.get("persistence_path")
    or first.get("output_path")
    or first.get("report_path")
)

if path_value:
    assert Path(path_value).exists()

print("AV5_PERSISTENCE_AND_REEXECUTION_OK")
