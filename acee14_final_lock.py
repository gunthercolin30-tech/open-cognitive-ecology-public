from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
with TemporaryDirectory() as tmp:
    r=AceeBestArchitectureArchive(root=Path(tmp)).step(inputs={"operation":"list_best_architectures"},persist=False)
    for key in ("selection_executed_by_archive","rollback_executed_by_archive","lineage_modified_by_archive","genealogy_modified_by_archive","publication_executed_by_archive","network_operation_executed"):
        assert r[key] is False
    assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
    for key in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven","collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven"):
        assert r[key] is False
print("ACEE_BEST_ARCHITECTURE_ARCHIVE_FINAL_LOCK_OK")
