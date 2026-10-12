from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


def main():
    try:
        ACEEMetaAnalysis().step(
            inputs={
                "observations": [
                    {
                        "observation_id": 1,
                        "effect_size": 0.1,
                        "variance": 1.0,
                    },
                    {
                        "observation_id": "1",
                        "effect_size": 0.2,
                        "variance": 1.0,
                    },
                ]
            },
            persist=False,
        )
    except ValueError as exc:
        assert str(exc) == (
            "duplicate_observation_id:1"
        )
    else:
        raise AssertionError(
            "cross-type observation collision accepted"
        )

    print(
        "ACEE19_CROSS_TYPE_OBSERVATION_ID_OK"
    )


if __name__ == "__main__":
    main()
