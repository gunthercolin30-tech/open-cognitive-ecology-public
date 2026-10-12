#!/usr/bin/env python3
from ontology.acee_meta_analysis import ACEEMetaAnalysis


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {"observation_id": "a", "effect_size": 0.2, "variance": 0.04},
                {"observation_id": "b", "effect_size": 0.4, "variance": 0.01},
            ]
        },
        persist=False,
    )
    assert result["pooled_effect"] == 0.36
    assert result["heterogeneity"]["degrees_of_freedom"] == 1
    assert ACEEMetaAnalysis().verify_meta_analysis(result)["verified"] is True
    print("ACEE19_FUNCTIONAL_TEST_OK")


if __name__ == "__main__":
    main()
