from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_dashboard import ACEEDashboard


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        dashboard = ACEEDashboard(
            root=root,
            runtime_dir=root / "runtime",
        )

        result = dashboard.step(
            inputs={
                "longitudinal_records": [
                    {
                        "cycle_id": "tamper-cycle",
                        "timestamp": "2026-07-14T13:00:00Z",
                        "before_score": 0.8,
                        "after_score": 0.9,
                        "decision": "accept",
                        "rollback_phase_completed": True,
                        "rollback_performed": False,
                    }
                ]
            },
            persist=False,
        )

        assert dashboard.verify_dashboard(result)["verified"]

        corrupted = deepcopy(result)
        corrupted["cycle_count"] = 999

        verification = dashboard.verify_dashboard(corrupted)

        assert verification["verified"] is False
        assert verification["verification_errors"]

    print("ACEE17_DASHBOARD_TAMPER_DETECTED")


if __name__ == "__main__":
    main()
