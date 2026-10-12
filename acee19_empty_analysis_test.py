from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


def main():
    result = ACEEMetaAnalysis().step(
        inputs={},
        persist=False,
    )

    assert result["observation_count"] == 0
    assert result["included_observation_count"] == 0
    assert result["excluded_observation_count"] == 0

    assert result["pooled_effect"] is None
    assert result["standard_error"] is None
    assert result["confidence_interval"] == {
        "lower": None,
        "upper": None,
    }

    assert (
        result["overall_significance"]
        == "insufficient_evidence"
    )
    assert (
        "no_valid_observations"
        in result["limitations"]
    )
    assert result["certification_performed"] is False

    print("ACEE19_EMPTY_ANALYSIS_OK")


if __name__ == "__main__":
    main()
