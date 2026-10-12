from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {
                    "observation_id": "positive",
                    "effect_size": 1.0,
                    "variance": 0.01,
                    "confidence": 0.95,
                },
                {
                    "observation_id": "negative",
                    "effect_size": -1.0,
                    "variance": 0.01,
                    "confidence": 0.95,
                },
                {
                    "observation_id": "neutral",
                    "effect_size": 0.0,
                    "variance": 0.01,
                    "confidence": 0.95,
                },
            ]
        },
        persist=False,
    )

    assert (
        result["heterogeneity"]["I2"]
        > 0.90
    )
    assert (
        "high_heterogeneity"
        in result["limitations"]
    )
    assert result["consistency_score"] < 0.10
    assert result["replication_support"] < 0.10
    assert result["certification_performed"] is False

    print("ACEE19_HIGH_HETEROGENEITY_OK")


if __name__ == "__main__":
    main()
