#!/usr/bin/env python3
from copy import deepcopy
from ontology.degeneration_detector import DegenerationDetector


def obs(day, value):
    return {
        "timestamp_utc": f"2027-05-{day:02d}T00:00:00Z",
        "state_vector": {k: value for k in ["stability", "integration", "continuity", "governance", "complexity", "diversity", "recovery_capacity", "openness"]},
        "data_quality": .99,
    }


def main():
    inputs = {"observations": [obs(1,.90), obs(2,.88), obs(3,.70), obs(4,.55), obs(5,.40)]}
    engine = DegenerationDetector()
    first = engine.step(inputs=inputs, persist=False)
    second = engine.step(inputs=deepcopy(inputs), persist=False)
    changed_inputs = deepcopy(inputs)
    changed_inputs["observations"][-1]["state_vector"]["openness"] = .20
    changed = engine.step(inputs=changed_inputs, persist=False)
    assert first["degeneration_hash"] == second["degeneration_hash"]
    assert first["degeneration_score"] == second["degeneration_score"]
    assert first["severity"] == second["severity"]
    assert first["affected_dimensions"] == second["affected_dimensions"]
    assert first["degeneration_hash"] != changed["degeneration_hash"]
    for result in (first, second, changed):
        assert result["consciousness_proven"] is False
        assert result["qualia_proven"] is False
        assert result["subjectivity_proven"] is False
        assert result["phenomenology_proven"] is False
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
    print("AV5_NON_REGRESSION_AND_DETERMINISM_OK")


if __name__ == "__main__":
    main()
