from ontology.comparative_dashboard import ComparativeDashboard
from ontology.comparative_history import ComparativeHistory


def main():
    dashboard = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    history = ComparativeHistory()

    first = history.step(
        inputs={
            "comparative_dashboard": dashboard,
        },
        persist=True,
    )

    second = history.step(
        inputs={
            "comparative_dashboard": dashboard,
        },
        persist=True,
    )

    assert first["comparative_history_ready"] is True
    assert second["comparative_history_ready"] is True

    assert second["change_set"]["change_type"] == "NO_CHANGE"
    assert second["append_required"] is False
    assert second["history_count_after"] == (
        second["history_count_before"]
    )

    print("AU9_NO_CHANGE_OK")


if __name__ == "__main__":
    main()
