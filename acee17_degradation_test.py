from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_dashboard import ACEEDashboard


def main():
    with TemporaryDirectory() as tmp:
        dash = ACEEDashboard(root=Path(tmp))
        result = dash.step(inputs={"timestamp_utc":"2026-07-14T12:00:00Z","records":[{"cycle_id":"C1","timestamp_utc":"2026-07-14T10:00:00Z","after_score":float("nan"),"decision":"unknown"}],"archives":[{"archive_id":"A","score":float("inf")} ]}, persist=False)
        assert result["status"] == "ACEE_DASHBOARD_READY"
        assert result["charts"]["cycle_score_over_time"][0]["after_score"] is None
        assert result["charts"]["accepted_vs_rejected_mutations"]["undetermined"] == 1
        assert "unknown_decision:unknown" in result["diagnostics"]["warnings"]
        assert result["charts"]["best_architecture_curve"] == []
    print("ACEE17_DEGRADATION_TEST_OK")


if __name__ == "__main__": main()
