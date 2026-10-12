from ontology.comparative_dashboard import ComparativeDashboard


def main():
    result = ComparativeDashboard().step(
        inputs={
            "taxonomy_builder": {
                "taxonomy_builder_status": (
                    "TAXONOMY_BUILDER_INCOMPLETE"
                ),
                "taxonomy_builder_ready": False,
                "taxonomy_entries": [],
            },
        },
        persist=False,
    )

    assert result["comparative_dashboard_ready"] is False
    assert result["comparative_dashboard_status"] == (
        "COMPARATIVE_DASHBOARD_INCOMPLETE"
    )
    assert result["dependencies_ready"] is False
    assert result["persisted"] is False

    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    print("AU8_DEGRADATION_OK")


if __name__ == "__main__":
    main()
