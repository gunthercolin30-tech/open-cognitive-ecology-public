from ontology.developmental_blueprint import DevelopmentalBlueprint


def main():
    original_axes = DevelopmentalBlueprint.developmental_axes

    try:
        DevelopmentalBlueprint.developmental_axes = []

        result = DevelopmentalBlueprint().step(
            inputs={},
            persist=False,
        )

        assert result["developmental_blueprint_ready"] is False
        assert result["developmental_blueprint_status"] == (
            "DEVELOPMENTAL_BLUEPRINT_INCOMPLETE"
        )

        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        assert result["consciousness_proven"] is False
        assert result["qualia_proven"] is False
        assert result["subjectivity_proven"] is False
        assert result["phenomenology_proven"] is False

        print("AV0_DEGRADATION_OK")

    finally:
        DevelopmentalBlueprint.developmental_axes = original_axes


if __name__ == "__main__":
    main()
