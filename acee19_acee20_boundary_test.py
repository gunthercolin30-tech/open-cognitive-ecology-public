from ontology.acee_meta_analysis import (
    ACEEMetaAnalysis,
)


FORBIDDEN_TRUE_FIELDS = {
    "certification_performed",
    "final_certification",
    "certified",
    "selection_performed",
    "execution_authorized",
    "schedule_created",
    "installation_completed",
    "mutation_executed",
    "rollback_performed",
    "consciousness_proven",
    "subjectivity_proven",
    "qualia_proven",
    "phenomenology_proven",
}


def inspect(value, path="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"

            if (
                key in FORBIDDEN_TRUE_FIELDS
                and item is True
            ):
                raise AssertionError(
                    f"forbidden_true:{child}"
                )

            inspect(item, child)

    elif isinstance(value, list):
        for index, item in enumerate(value):
            inspect(
                item,
                f"{path}[{index}]",
            )


def main():
    result = ACEEMetaAnalysis().step(
        inputs={
            "observations": [
                {
                    "observation_id": "strong-1",
                    "effect_size": 1.0,
                    "variance": 0.0001,
                    "confidence": 1.0,
                    "validation_status": "passed",
                    "causal_status": "resolved",
                    "stability_score": 1.0,
                },
                {
                    "observation_id": "strong-2",
                    "effect_size": 1.0,
                    "variance": 0.0001,
                    "confidence": 1.0,
                    "validation_status": "passed",
                    "causal_status": "resolved",
                    "stability_score": 1.0,
                },
                {
                    "observation_id": "strong-3",
                    "effect_size": 1.0,
                    "variance": 0.0001,
                    "confidence": 1.0,
                    "validation_status": "passed",
                    "causal_status": "resolved",
                    "stability_score": 1.0,
                },
            ]
        },
        persist=False,
    )

    inspect(result)

    assert result["overall_significance"] == "p<0.001"
    assert result["functional_conclusion_only"] is True
    assert result["certification_performed"] is False

    print("ACEE19_ACEE20_BOUNDARY_OK")


if __name__ == "__main__":
    main()
