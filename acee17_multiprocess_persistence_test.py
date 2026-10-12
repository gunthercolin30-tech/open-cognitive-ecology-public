import json
import multiprocessing
from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_dashboard import ACEEDashboard


def worker(root_text, index):
    root = Path(root_text)
    runtime = root / "acee_runtime" / "ACEE17_acee_dashboard"
    ACEEDashboard(root=root, runtime_dir=runtime).step(
        inputs={
            "records": [
                {
                    "cycle_id": f"process-{index}",
                    "timestamp_utc": f"2026-07-14T12:00:0{index}Z",
                    "before_score": 0.80,
                    "after_score": 0.81 + index / 100,
                    "decision": "accept",
                    "rollback_phase_completed": True,
                    "rollback_performed": False,
                    "metrics": {
                        "error_count": 0,
                        "evolution_score": 0.81 + index / 100,
                        "governance_score": 0.90,
                        "closure_pressure": 0.10,
                        "stability_score": 0.94,
                        "causal_impact": 0.01 + index / 100,
                    },
                }
            ],
        },
        persist=True,
    )


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        processes = [
            multiprocessing.Process(target=worker, args=(str(root), index))
            for index in range(4)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
            assert process.exitcode == 0

        runtime = root / "acee_runtime" / "ACEE17_acee_dashboard"
        json_path = runtime / "latest_dashboard.json"
        html_path = runtime / "latest_dashboard.html"
        assert json_path.exists()
        assert html_path.exists()

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        verification = ACEEDashboard(
            root=root,
            runtime_dir=runtime,
        ).verify_dashboard(payload)

        assert payload["status"] == "ACEE_DASHBOARD_READY"
        assert payload["persist_requested"] is True
        assert payload["persisted"] is True
        assert Path(
            payload["artifacts"]["json_path"]
        ).resolve() == json_path.resolve()
        assert Path(
            payload["artifacts"]["html_path"]
        ).resolve() == html_path.resolve()
        assert payload["exports"]["json"] is None
        assert verification["verified"] is True
        assert html_path.stat().st_size > 0

    print("ACEE17_MULTIPROCESS_PERSISTENCE_OK")


if __name__ == "__main__":
    main()
