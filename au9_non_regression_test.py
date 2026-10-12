import tempfile
from pathlib import Path

from ontology.comparative_dashboard import ComparativeDashboard
from ontology.comparative_history import ComparativeHistory


def main():
    dashboard = ComparativeDashboard().step(
        inputs={},
        persist=False,
    )

    with tempfile.TemporaryDirectory(
        prefix="oce_au9_non_regression_"
    ) as tmp:
        history = ComparativeHistory(
            root=Path(tmp),
        )

        first = history.step(
            inputs={
                "comparative_dashboard": dashboard,
            },
            persist=False,
        )

        second = history.step(
            inputs={
                "comparative_dashboard": dashboard,
            },
            persist=False,
        )

    assert first["snapshot_hash"] == second["snapshot_hash"]
    assert first["change_set"] == second["change_set"]

    assert first["persisted"] is False
    assert second["persisted"] is False
    assert first["output_paths"] == {}
    assert second["output_paths"] == {}

    print("AU9_NON_REGRESSION_AND_DETERMINISM_OK")


if __name__ == "__main__":
    main()
