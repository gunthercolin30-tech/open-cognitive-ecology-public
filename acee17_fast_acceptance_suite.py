from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_dashboard import ACEEDashboard, REQUIRED_CHARTS


def fixture():
    return {
        "timestamp_utc": "2026-07-14T12:00:00Z",
        "records": [
            {"record_id":"R2","cycle_id":"C2","timestamp_utc":"2026-07-14T11:00:00Z","before_score":0.8,"after_score":0.82,"score_delta":0.02,"error_count":0,"evolution_score":0.81,"governance_score":0.92,"rollback_phase_completed":True,"rollback_performed":False,"decision":"accept","causal_score":0.7,"closure_pressure":0.2,"stability_score":0.93},
            {"record_id":"R1","cycle_id":"C1","timestamp_utc":"2026-07-14T10:00:00Z","before_score":0.7,"after_score":0.8,"score_delta":0.1,"error_count":0,"evolution_score":0.78,"governance_score":0.91,"rollback_phase_completed":True,"rollback_performed":True,"decision":"rollback","causal_score":0.6,"closure_pressure":0.25,"stability_score":0.9},
        ],
        "genealogy": {"lineage_tree":{"root":"G0","children":["G1"]}},
        "archive": {"archives":[{"archive_id":"A1","timestamp_utc":"2026-07-14T10:30:00Z","architecture_score":0.8},{"archive_id":"A2","timestamp_utc":"2026-07-14T11:30:00Z","architecture_score":0.85}]},
    }


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        dash = ACEEDashboard(root=root)
        result = dash.step(inputs=fixture(), persist=False)
        assert result["status"] == "ACEE_DASHBOARD_READY"
        assert result["dashboard_ready"] is True
        assert result["cycle_count"] == 2
        assert set(result["charts"]) == set(REQUIRED_CHARTS)
        assert result["charts"]["cycle_score_over_time"][0]["cycle_id"] == "C1"
        rollbacks = result["charts"]["rollback_count_over_time"]
        assert rollbacks[-1]["rollback_count"] == 1
        assert result["charts"]["accepted_vs_rejected_mutations"]["accept"] == 1
        assert result["charts"]["accepted_vs_rejected_mutations"]["rollback"] == 1
        assert result["persisted"] is False
        assert not (root / "acee_runtime").exists()
        repeat = dash.step(inputs=fixture(), persist=False)
        assert repeat["dashboard_hash"] == result["dashboard_hash"]
    print("ACEE17_FAST_ACCEPTANCE_OK")


if __name__ == "__main__": main()
