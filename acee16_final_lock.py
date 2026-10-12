from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_longitudinal_tracker import AceeLongitudinalTracker

def main():
    with TemporaryDirectory() as tmp:
        result = AceeLongitudinalTracker(root=Path(tmp)).step(inputs={"operation":"list_cycles"}, persist=False)
        for key in ["cycle_executed_by_tracker","validation_executed_by_tracker","impact_recomputed_by_tracker","causality_recomputed_by_tracker","selection_executed_by_tracker","rollback_executed_by_tracker","scheduling_modified_by_tracker","lineage_modified_by_tracker","archive_modified_by_tracker"]: assert result[key] is False
        assert result["functional_conclusion_only"] is True and result["phenomenology_undetermined"] is True
        for key in ["consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven","collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven"]: assert result[key] is False
    print("ACEE_LONGITUDINAL_TRACKER_FINAL_LOCK_OK")
if __name__ == "__main__": main()
