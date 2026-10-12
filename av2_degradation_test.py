from ontology.maturation_tracker import MaturationTracker

GENESIS = {"genesis_detected": True, "genesis_status": "FUNCTIONAL_GENESIS_DETECTED"}


def obs(index, value, quality=0.95):
    return {
        "timestamp_utc": f"2026-05-{index:02d}T00:00:00Z",
        "stability": value, "integration": value, "continuity": value,
        "governance": value, "complexity": value, "diversity": value,
        "recovery": value, "data_quality": quality, "synthetic": True,
    }


def main():
    missing = MaturationTracker().step(inputs={}, persist=False)
    assert missing["maturation_status"] == "FUNCTIONAL_MATURATION_UNDETERMINED"

    no_genesis = MaturationTracker().step(inputs={"observations": [obs(i, 0.8) for i in range(1, 7)]}, persist=False)
    assert no_genesis["maturation_status"] == "FUNCTIONAL_MATURATION_NOT_ESTABLISHED"

    plateau = MaturationTracker().step(inputs={"genesis_result": GENESIS, "observations": [obs(i, v) for i, v in enumerate([0.72, 0.73, 0.72, 0.73, 0.72, 0.73], 1)]}, persist=False)
    assert plateau["plateau_detected"] is True
    assert plateau["maturation_status"] == "FUNCTIONAL_MATURATION_PLATEAU"

    regression = MaturationTracker().step(inputs={"genesis_result": GENESIS, "observations": [obs(i, v) for i, v in enumerate([0.90, 0.84, 0.76, 0.66, 0.55, 0.45], 1)]}, persist=False)
    assert regression["regression_detected"] is True
    assert regression["maturation_status"] == "FUNCTIONAL_MATURATION_REGRESSING"

    low_quality = MaturationTracker().step(inputs={"genesis_result": GENESIS, "observations": [obs(i, 0.85, 0.2) for i in range(1, 7)]}, persist=False)
    assert low_quality["maturation_status"] == "FUNCTIONAL_MATURATION_UNDETERMINED"

    invalid_time = {"genesis_result": GENESIS, "observations": [obs(3, 0.6), obs(1, 0.7), obs(2, 0.8), obs(4, 0.85), obs(5, 0.9)]}
    invalid = MaturationTracker().step(inputs=invalid_time, persist=False)
    assert invalid["maturation_status"] == "FUNCTIONAL_MATURATION_UNDETERMINED"
    assert invalid["condition_results"]["explicit_time_order"] is False

    for result in [missing, no_genesis, plateau, regression, low_quality, invalid]:
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        assert result["consciousness_proven"] is False
    print("AV2_DEGRADATION_OK")


if __name__ == "__main__":
    main()
