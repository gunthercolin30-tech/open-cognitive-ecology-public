from pathlib import Path
from tempfile import TemporaryDirectory
from ontology import dna_versioning_lineage as d
with TemporaryDirectory() as td:
 p=Path(td)/"institution.json"; x=d.create_lineage("INST-1",d.INSTITUTION,"DNA-A",provenance="restart")
 x=d.migrate_lineage(x,migration_id="M1",to_DNA="DNA-B",mutation_ref="P021:M1",evidence_refs=("E1",),authority_ref="AUTH",provenance="restart")
 d.save_lineage(p,x); y=d.load_lineage(p); z=d.load_lineage(p)
 assert y==x and z["created_under_DNA"]=="DNA-A" and z["current_DNA"]=="DNA-B" and len(z["migration_history"])==1
print("P022_PERSISTENCE_RESTART_TEST_OK")
