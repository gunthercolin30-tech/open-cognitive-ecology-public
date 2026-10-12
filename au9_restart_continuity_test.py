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
        prefix="oce_au9_restart_"
    ) as tmp:
        root = Path(tmp)

        first_instance = ComparativeHistory(root=root)

        first = first_instance.step(
            inputs={
                "comparative_dashboard": dashboard,
            },
            persist=True,
        )

        second_instance = ComparativeHistory(root=root)

        second = second_instance.step(
            inputs={
                "comparative_dashboard": dashboard,
            },
            persist=True,
        )

        assert first["history_count_after"] == 1
        assert second["change_set"]["change_type"] == "NO_CHANGE"
        assert second["append_required"] is False
        assert second["history_count_before"] == 1
        assert second["history_count_after"] == 1
        assert second["chain_integrity"]["chain_valid"] is True

    print("AU9_RESTART_CONTINUITY_OK")


if __name__ == "__main__":
    main()
