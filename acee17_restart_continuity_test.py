import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_dashboard import ACEEDashboard


def main():
    inputs = {
        "records": [
            {
                "cycle_id": "restart-cycle",
                "timestamp_utc": "2026-07-14T12:00:00Z",
                "before_score": 0.80,
                "after_score": 0.85,
                "decision": "accept",
                "rollback_phase_completed": True,
                "rollback_performed": False,
                "metrics": {
                    "error_count": 0,
                    "evolution_score": 0.85,
                    "governance_score": 0.91,
                    "closure_pressure": 0.08,
                    "stability_score": 0.95,
                    "causal_impact": 0.05,
                },
            }
        ],
    }

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        runtime = root / "acee_runtime" / "ACEE17_acee_dashboard"
        first = ACEEDashboard(root=root, runtime_dir=runtime).step(
            inputs=inputs,
            persist=True,
        )
        first_hash = first["dashboard_hash"]

        second_dashboard = ACEEDashboard(root=root, runtime_dir=runtime)
        persisted = json.loads(
            (runtime / "latest_dashboard.json").read_text(encoding="utf-8")
        )
        verification = second_dashboard.verify_dashboard(persisted)

        assert verification["verified"] is True
        assert persisted["dashboard_hash"] == first_hash
        assert persisted["cycle_count"] == 1
        assert persisted["persist_requested"] is True
        assert persisted["persisted"] is True
        assert Path(
            persisted["artifacts"]["json_path"]
        ).resolve() == (
            runtime / "latest_dashboard.json"
        ).resolve()
        assert Path(
            persisted["artifacts"]["html_path"]
        ).resolve() == (
            runtime / "latest_dashboard.html"
        ).resolve()
        assert persisted["exports"]["json"] is None

    print("ACEE17_RESTART_CONTINUITY_OK")


if __name__ == "__main__":
    main()
