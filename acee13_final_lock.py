from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    r=AceeLineageManager(root=Path(tmp)).step({"operation":"inspect"},persist=False)
    assert r["selection_executed_by_lineage_manager"] is False
    assert r["rollback_executed_by_lineage_manager"] is False
    assert r["mutation_executed_by_lineage_manager"] is False
    assert r["genealogy_written_by_lineage_manager"] is False
    assert r["best_architecture_archived"] is False
    assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
    for k in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven","collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven"):
        assert r[k] is False
print("ACEE_LINEAGE_MANAGER_FINAL_LOCK_OK")
