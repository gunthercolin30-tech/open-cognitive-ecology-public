from ontology.comparative_dashboard import ComparativeDashboard


def main():
    first = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )
    second = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    assert first["dashboard_hash"] == second["dashboard_hash"]
    assert first["dashboard_summary"] == second["dashboard_summary"]
    assert first["module_statuses"] == second["module_statuses"]

    assert first["persisted"] is False
    assert second["persisted"] is False
    assert first["output_paths"] == {}
    assert second["output_paths"] == {}

    for result in (first, second):
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        assert result["consciousness_proven"] is False
        assert result["qualia_proven"] is False
        assert result["subjectivity_proven"] is False
        assert result["phenomenology_proven"] is False

    print("AU8_NON_REGRESSION_AND_DETERMINISM_OK")


if __name__ == "__main__":
    main()
