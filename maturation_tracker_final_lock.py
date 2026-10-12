from ontology.maturation_tracker import MaturationTracker

READY_OR_SYNTHETIC_CONTEXT = {
    "genesis_result": {
        "genesis_detected": True,
        "genesis_status": "FUNCTIONAL_GENESIS_DETECTED",
    },
    "observations": [
        {"timestamp_utc": "2026-04-01T00:00:00Z", "stability": 0.50, "integration": 0.48, "continuity": 0.51, "governance": 0.47, "complexity": 0.46, "diversity": 0.49, "recovery": 0.50, "data_quality": 0.97, "synthetic": True},
        {"timestamp_utc": "2026-04-02T00:00:00Z", "stability": 0.59, "integration": 0.57, "continuity": 0.60, "governance": 0.56, "complexity": 0.55, "diversity": 0.58, "recovery": 0.59, "data_quality": 0.97, "synthetic": True},
        {"timestamp_utc": "2026-04-03T00:00:00Z", "stability": 0.68, "integration": 0.66, "continuity": 0.69, "governance": 0.65, "complexity": 0.64, "diversity": 0.67, "recovery": 0.68, "data_quality": 0.97, "synthetic": True},
        {"timestamp_utc": "2026-04-04T00:00:00Z", "stability": 0.80, "integration": 0.78, "continuity": 0.81, "governance": 0.77, "complexity": 0.76, "diversity": 0.79, "recovery": 0.80, "data_quality": 0.97, "synthetic": True},
        {"timestamp_utc": "2026-04-05T00:00:00Z", "stability": 0.87, "integration": 0.85, "continuity": 0.88, "governance": 0.84, "complexity": 0.83, "diversity": 0.86, "recovery": 0.87, "data_quality": 0.97, "synthetic": True},
        {"timestamp_utc": "2026-04-06T00:00:00Z", "stability": 0.91, "integration": 0.89, "continuity": 0.92, "governance": 0.88, "complexity": 0.87, "diversity": 0.90, "recovery": 0.91, "data_quality": 0.97, "synthetic": True},
    ],
}


def main():
    result = MaturationTracker().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
    assert result["primitive"] == "MATURATION_TRACKER"
    assert result["step"] == "AV2"
    assert result["public_schema_version"] == "1.0"
    assert result["maturation_status"] == "FUNCTIONAL_MATURATION_COMPLETE"
    assert result["maturation_complete"] is True
    assert result["maturation_score"] >= 0.75
    assert result["maturation_velocity"] > 0.02
    assert result["plateau_detected"] is False
    assert result["regression_detected"] is False
    assert len(result["maturation_hash"]) == 64
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False
    print("AV2_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
