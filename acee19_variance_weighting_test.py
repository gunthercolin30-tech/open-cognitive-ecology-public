from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {
                    "observation_id": "precise",
                    "effect_size": 0.80,
                    "variance": 0.01,
                },
                {
                    "observation_id": "imprecise",
                    "effect_size": -0.80,
                    "variance": 1.00,
                },
            ]
        },
        persist=False,
    )

    assert result["pooled_effect"] > 0.70

    observations = {
        item["observation_id"]: item
        for item in result["included_observations"]
    }

    assert (
        observations["precise"]["weight"]
        >
        observations["imprecise"]["weight"]
    )

    print("ACEE19_VARIANCE_WEIGHTING_OK")


if __name__ == "__main__":
    main()
