from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_autonomous_scheduler import AceeAutonomousScheduler

def main():
    with TemporaryDirectory() as tmp:
        result = AceeAutonomousScheduler(root=Path(tmp)).step(inputs={"operation":"inspect_schedule"}, persist=False)
        assert result["cycle_executed_by_scheduler"] is False
        assert result["acee4_executed_by_scheduler"] is False
        assert result["validation_main_executed"] is False
        assert result["rollback_executed"] is False
        assert result["selection_executed"] is False
        assert result["lineage_modified"] is False
        assert result["archive_modified"] is False
        assert result["network_operation_executed"] is False
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True
    print("ACEE_AUTONOMOUS_SCHEDULER_FINAL_LOCK_OK")
if __name__ == "__main__": main()
