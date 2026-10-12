from pathlib import Path

from ontology.bifurcation_detector import BifurcationDetector


def observation(day, value):
    return {
        "timestamp_utc": f"2027-01-{day:02d}T00:00:00Z",
        "state_vector": {
            "stability": value,
            "integration": value,
            "continuity": value,
            "specialization": 1.0 - value,
            "diversity": value,
            "openness": value,
        },
        "data_quality": 0.98,
    }


inputs = {
    "observations": [
        observation(1, 0.82),
        observation(2, 0.80),
        observation(3, 0.45),
        observation(4, 0.44),
        observation(5, 0.43),
    ],
}

detector = BifurcationDetector()

first = detector.step(inputs=inputs, persist=True)
second = detector.step(inputs=inputs, persist=True)

assert first["bifurcation_hash"] == second["bifurcation_hash"]
assert first["bifurcation_status"] == second["bifurcation_status"]
assert first["structural_break_score"] == second[
    "structural_break_score"
]
assert first["pre_regime"] == second["pre_regime"]
assert first["post_regime"] == second["post_regime"]

path_value = (
    first.get("persistence_path")
    or first.get("output_path")
    or first.get("report_path")
)

if path_value:
    assert Path(path_value).exists()

print("AV4_PERSISTENCE_AND_REEXECUTION_OK")
