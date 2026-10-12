from ontology.genesis_detector import GenesisDetector


def main():
    cases = {
        "missing": {},
        "isolated_crossing": {"observations": [
            {"timestamp_utc": "t0", "rf_star_score": 0.25, "data_quality": 0.9},
            {"timestamp_utc": "t1", "rf_star_score": 0.85, "data_quality": 0.9},
            {"timestamp_utc": "t2", "rf_star_score": 0.30, "data_quality": 0.9},
            {"timestamp_utc": "t3", "rf_star_score": 0.32, "data_quality": 0.9},
            {"timestamp_utc": "t4", "rf_star_score": 0.35, "data_quality": 0.9},
        ]},
        "already_high_baseline": {
            "baseline": [0.80, 0.82],
            "observations": [
                {"timestamp_utc": "t0", "rf_star_score": 0.82, "data_quality": 0.9},
                {"timestamp_utc": "t1", "rf_star_score": 0.84, "data_quality": 0.9},
                {"timestamp_utc": "t2", "rf_star_score": 0.86, "data_quality": 0.9},
                {"timestamp_utc": "t3", "rf_star_score": 0.88, "data_quality": 0.9},
                {"timestamp_utc": "t4", "rf_star_score": 0.89, "data_quality": 0.9},
            ],
        },
        "low_quality": {"observations": [
            {"timestamp_utc": "t0", "rf_star_score": 0.25, "data_quality": 0.2},
            {"timestamp_utc": "t1", "rf_star_score": 0.30, "data_quality": 0.2},
            {"timestamp_utc": "t2", "rf_star_score": 0.84, "stability": 0.9, "continuity": 0.9, "coherence": 0.9, "data_quality": 0.2},
            {"timestamp_utc": "t3", "rf_star_score": 0.86, "stability": 0.9, "continuity": 0.9, "coherence": 0.9, "data_quality": 0.2},
            {"timestamp_utc": "t4", "rf_star_score": 0.88, "stability": 0.9, "continuity": 0.9, "coherence": 0.9, "data_quality": 0.2},
        ]},
        "noisy": {"observations": [
            {"timestamp_utc": f"t{i}", "rf_star_score": score, "data_quality": 0.9}
            for i, score in enumerate([0.2, 0.8, 0.3, 0.82, 0.35, 0.84, 0.4])
        ]},
    }
    for name, payload in cases.items():
        result = GenesisDetector().step(inputs=payload, persist=False)
        assert result["genesis_detected"] is False, name
        assert result["genesis_status"] != "FUNCTIONAL_GENESIS_DETECTED", name
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        assert result["consciousness_proven"] is False
    print("AV1_DEGRADATION_OK")


if __name__ == "__main__":
    main()
