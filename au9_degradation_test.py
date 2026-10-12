from ontology.comparative_history import ComparativeHistory


def main():
    result = ComparativeHistory().step(
        inputs={
            "comparative_dashboard": {
                "comparative_dashboard_status": (
                    "COMPARATIVE_DASHBOARD_INCOMPLETE"
                ),
                "comparative_dashboard_ready": False,
            },
        },
        persist=False,
    )

    assert result["comparative_history_status"] == (
        "COMPARATIVE_HISTORY_INCOMPLETE"
    )
    assert result["comparative_history_ready"] is False
    assert result["dashboard_ready"] is False
    assert result["persisted"] is False
    assert result["output_paths"] == {}

    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
    assert result["consciousness_proven"] is False
    assert result["qualia_proven"] is False
    assert result["subjectivity_proven"] is False
    assert result["phenomenology_proven"] is False

    print("AU9_DEGRADATION_OK")


if __name__ == "__main__":
    main()
