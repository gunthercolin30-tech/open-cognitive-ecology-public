from ontology.comparative_dashboard import ComparativeDashboard


def main():
    dashboard = ComparativeDashboard()

    transient = dashboard.step(
        inputs={},
        persist=False,
    )

    persisted = dashboard.step(
        inputs={},
        persist=True,
    )

    assert transient["dashboard_hash"] == persisted["dashboard_hash"]

    assert transient["timestamp_utc"] != ""
    assert persisted["timestamp_utc"] != ""

    assert transient["persisted"] is False
    assert persisted["persisted"] is True

    assert transient["output_paths"] == {}
    assert persisted["output_paths"]

    print("AU8_HASH_SCOPE_OK")


if __name__ == "__main__":
    main()
