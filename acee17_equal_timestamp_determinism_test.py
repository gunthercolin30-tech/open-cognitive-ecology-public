from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_dashboard import ACEEDashboard


def record(cycle_id):
    return {
        "cycle_id": cycle_id,
        "timestamp": "2026-07-14T14:00:00Z",
        "before_score": 0.8,
        "after_score": 0.81,
        "decision": "accept",
        "rollback_phase_completed": True,
        "rollback_performed": False,
    }


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        dashboard = ACEEDashboard(
            root=root,
            runtime_dir=root / "runtime",
        )

        first = dashboard.step(
            inputs={
                "longitudinal_records": [
                    record("cycle-b"),
                    record("cycle-a"),
                    record("cycle-c"),
                ]
            },
            persist=False,
        )

        second = dashboard.step(
            inputs={
                "longitudinal_records": [
                    record("cycle-c"),
                    record("cycle-b"),
                    record("cycle-a"),
                ]
            },
            persist=False,
        )

        assert first["dashboard_hash"] == second["dashboard_hash"]

        first_ids = [
            item["cycle_id"]
            for item in first["charts"][
                "cycle_score_over_time"
            ]
        ]

        second_ids = [
            item["cycle_id"]
            for item in second["charts"][
                "cycle_score_over_time"
            ]
        ]

        assert first_ids == second_ids

    print("ACEE17_EQUAL_TIMESTAMP_DETERMINISM_OK")


if __name__ == "__main__":
    main()
