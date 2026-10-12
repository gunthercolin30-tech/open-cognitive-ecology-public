from copy import deepcopy
from ontology.maturation_tracker import MaturationTracker

CONTEXT = {
    "genesis_result": {"genesis_detected": True, "genesis_status": "FUNCTIONAL_GENESIS_DETECTED"},
    "observations": [
        {"timestamp_utc": f"2026-06-{i:02d}T00:00:00Z", "stability": v, "integration": v, "continuity": v, "governance": v, "complexity": v, "diversity": v, "recovery": v, "data_quality": 0.95}
        for i, v in enumerate([0.50, 0.58, 0.66, 0.74, 0.82, 0.88], 1)
    ],
}


def main():
    tracker = MaturationTracker()
    first = tracker.step(inputs=deepcopy(CONTEXT), persist=False)
    second = tracker.step(inputs=deepcopy(CONTEXT), persist=False)
    assert first["maturation_hash"] == second["maturation_hash"]
    assert first["maturation_score"] == second["maturation_score"]
    assert first["maturation_velocity"] == second["maturation_velocity"]
    assert first["dimension_scores"] == second["dimension_scores"]
    assert first["condition_results"] == second["condition_results"]
    assert first["maturation_status"] == "FUNCTIONAL_MATURATION_COMPLETE"

    perturbed = deepcopy(CONTEXT)
    perturbed["observations"][4]["complexity"] = 0.78
    changed = tracker.step(inputs=perturbed, persist=False)
    assert changed["maturation_hash"] != first["maturation_hash"]
    assert changed["maturation_status"] == "FUNCTIONAL_MATURATION_COMPLETE"

    for result in (first, second, changed):
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        assert result["consciousness_proven"] is False
        assert result["qualia_proven"] is False
        assert result["subjectivity_proven"] is False
        assert result["phenomenology_proven"] is False
    print("AV2_NON_REGRESSION_AND_DETERMINISM_OK")


if __name__ == "__main__":
    main()
