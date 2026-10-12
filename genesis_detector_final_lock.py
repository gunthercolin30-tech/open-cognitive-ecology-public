from ontology.genesis_detector import GenesisDetector

READY_OR_SYNTHETIC_CONTEXT = {
    "observations": [
        {"timestamp_utc": "2026-02-01T00:00:00Z", "rf_star_score": 0.28, "stability": 0.55, "continuity": 0.55, "coherence": 0.55, "data_quality": 0.96, "synthetic": True, "source": "av1_lock"},
        {"timestamp_utc": "2026-02-02T00:00:00Z", "rf_star_score": 0.34, "stability": 0.58, "continuity": 0.58, "coherence": 0.58, "data_quality": 0.96, "synthetic": True, "source": "av1_lock"},
        {"timestamp_utc": "2026-02-03T00:00:00Z", "rf_star_score": 0.85, "stability": 0.89, "continuity": 0.87, "coherence": 0.90, "data_quality": 0.96, "synthetic": True, "source": "av1_lock"},
        {"timestamp_utc": "2026-02-04T00:00:00Z", "rf_star_score": 0.88, "stability": 0.91, "continuity": 0.89, "coherence": 0.92, "data_quality": 0.96, "synthetic": True, "source": "av1_lock"},
        {"timestamp_utc": "2026-02-05T00:00:00Z", "rf_star_score": 0.90, "stability": 0.92, "continuity": 0.91, "coherence": 0.93, "data_quality": 0.96, "synthetic": True, "source": "av1_lock"},
    ]
}


def main():
    result = GenesisDetector().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert result["primitive"] == "GENESIS_DETECTOR"
    assert result["step"] == "AV1"
    assert result["public_schema_version"] == "1.0"
    assert result["genesis_detected"] is True
    assert result["genesis_status"] == "FUNCTIONAL_GENESIS_DETECTED"
    assert result["genesis_timestamp"] == "2026-02-03T00:00:00Z"
    assert result["genesis_score"] >= 0.70
    assert result["genesis_confidence"] >= 0.70
    assert result["false_positive_risk"] <= 0.35
    assert len(result["genesis_hash"]) == 64
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    print("AV1_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
