from pathlib import Path

from ontology.genesis_detector import GenesisDetector


def observation(day, score):
    return {
        "timestamp_utc": f"2026-02-{day:02d}T00:00:00Z",
        "rf_star_score": score,
        "stability": 0.91,
        "continuity": 0.92,
        "coherence": 0.93,
        "data_quality": 0.97,
        "synthetic": True,
    }


inputs = {
    "observations": [
        observation(1, 0.20),
        observation(2, 0.25),
        observation(3, 0.85),
        observation(4, 0.88),
        observation(5, 0.90),
    ],
    "baseline": [
        observation(1, 0.20),
        observation(2, 0.25),
    ],
}

detector = GenesisDetector()

first = detector.step(
    inputs=inputs,
    persist=True,
)

second = detector.step(
    inputs=inputs,
    persist=True,
)

assert first["genesis_hash"] == second["genesis_hash"]
assert first["genesis_status"] == second["genesis_status"]

path_value = (
    first.get("persistence_path")
    or first.get("output_path")
    or first.get("report_path")
)

if path_value:
    assert Path(path_value).exists()

print("AV1_PERSISTENCE_AND_REEXECUTION_OK")
