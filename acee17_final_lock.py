from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_dashboard import ACEEDashboard, REQUIRED_CHARTS


def main():
    with TemporaryDirectory() as tmp:
        result = ACEEDashboard(root=Path(tmp)).step(inputs={"timestamp_utc":"2026-07-14T12:00:00Z","records":[]}, persist=False)
        assert result["status"] == "ACEE_DASHBOARD_READY"
        assert result["dashboard_ready"] is True
        assert set(result["charts"]) == set(REQUIRED_CHARTS)
        for key in ["cycle_executed_by_dashboard","validation_executed_by_dashboard","impact_recomputed_by_dashboard","causality_recomputed_by_dashboard","selection_executed_by_dashboard","rollback_executed_by_dashboard","lineage_modified_by_dashboard","archive_modified_by_dashboard"]:
            assert result[key] is False
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
        for key in ["consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven","collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven"]:
            assert result[key] is False
    print("ACEE_DASHBOARD_FINAL_LOCK_OK")


if __name__ == "__main__": main()
