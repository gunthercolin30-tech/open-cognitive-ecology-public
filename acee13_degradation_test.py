from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    r=AceeLineageManager(root=Path(tmp)).step({"operation":"register_candidate","transaction_id":"T","lineage_id":"L","generation_id":1,"architecture_id":"A","parent_id":"MISSING","mutation_id":"M","fitness_delta":0.1},persist=False)
    assert not r["lineage_management_ready"] and "lineage_not_found" in r["blocking_reasons"]
print("ACEE13_DEGRADATION_OK")
