from ontology.acee_dashboard import ACEEDashboard


def main():
    result = ACEEDashboard().step(
        inputs={},
        persist=True,
    )

    assert result["status"] == "ACEE_DASHBOARD_READY"
    assert result["dashboard_ready"] is True
    assert result["persist_requested"] is True
    assert result["persisted"] is True
    assert result["artifacts"]["json_path"]
    assert result["artifacts"]["html_path"]

    print("ACEE17_PERSISTED_DASHBOARD_GENERATED")


if __name__ == "__main__":
    main()
