from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_best_architecture_archive import AceeBestArchitectureArchive
with TemporaryDirectory() as tmp:
    r=AceeBestArchitectureArchive(root=Path(tmp)).step(inputs={"operation":"archive_architecture"},persist=True)
    assert r["archive_ready"] is False and "accepted_selection_required" in r["blocking_reasons"]
print("ACEE14_DEGRADATION_OK")
