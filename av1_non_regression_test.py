from copy import deepcopy
from ontology.genesis_detector import GenesisDetector

CONTEXT = {
    "observations": [
        {"timestamp_utc": "t0", "rf_star_score": 0.25, "stability": 0.55, "continuity": 0.55, "coherence": 0.55, "data_quality": 0.95},
        {"timestamp_utc": "t1", "rf_star_score": 0.32, "stability": 0.58, "continuity": 0.58, "coherence": 0.58, "data_quality": 0.95},
        {"timestamp_utc": "t2", "rf_star_score": 0.85, "stability": 0.88, "continuity": 0.86, "coherence": 0.90, "data_quality": 0.95},
        {"timestamp_utc": "t3", "rf_star_score": 0.87, "stability": 0.90, "continuity": 0.88, "coherence": 0.91, "data_quality": 0.95},
        {"timestamp_utc": "t4", "rf_star_score": 0.90, "stability": 0.92, "continuity": 0.90, "coherence": 0.93, "data_quality": 0.95},
    ]
}


def main():
    detector = GenesisDetector()
    first = detector.step(inputs=deepcopy(CONTEXT), persist=False)
    second = detector.step(inputs=deepcopy(CONTEXT), persist=False)
    assert first["genesis_hash"] == second["genesis_hash"]
    assert first["genesis_score"] == second["genesis_score"]
    assert first["genesis_confidence"] == second["genesis_confidence"]
    assert first["genesis_window"] == second["genesis_window"]
    assert first["condition_results"] == second["condition_results"]
    assert first["genesis_detected"] is True

    perturbed = deepcopy(CONTEXT)
    perturbed["observations"][3]["rf_star_score"] = 0.88
    changed = detector.step(inputs=perturbed, persist=False)
    assert changed["genesis_hash"] != first["genesis_hash"]
    assert changed["genesis_detected"] is True

    for result in (first, second, changed):
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        assert result["consciousness_proven"] is False
        assert result["qualia_proven"] is False
        assert result["subjectivity_proven"] is False
        assert result["phenomenology_proven"] is False
    print("AV1_NON_REGRESSION_AND_DETERMINISM_OK")


if __name__ == "__main__":
    main()
