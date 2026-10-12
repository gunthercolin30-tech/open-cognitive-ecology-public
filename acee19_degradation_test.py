#!/usr/bin/env python3
from ontology.acee_meta_analysis import ACEEMetaAnalysis


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {"observation_id": "nan", "effect_size": float("nan"), "variance": 1.0},
                {"observation_id": "inf", "effect_size": float("inf"), "variance": 1.0},
                {"observation_id": "zero", "effect_size": 0.2, "variance": 0.0},
                {"observation_id": "valid", "effect_size": 0.1, "variance": 1.0},
            ]
        },
        persist=False,
    )
    assert result["observation_count"] == 4
    assert result["included_observation_count"] == 1
    assert result["excluded_observation_count"] == 3
    assert result["overall_significance"] == "insufficient_evidence"
    assert "single_observation_no_meta_inference" in result["limitations"]
    print("ACEE19_DEGRADATION_TEST_OK")


if __name__ == "__main__":
    main()
