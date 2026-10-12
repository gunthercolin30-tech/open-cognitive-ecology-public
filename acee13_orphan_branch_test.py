import json
from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    manager = AceeLineageManager(root=root)
    manager.step(inputs={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}, persist=True)
    history = root / "acee_runtime" / "ACEE13_acee_lineage_manager" / "lineage_event_history.jsonl"
    before = history.read_bytes()
    refused = manager.step(inputs={"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":2,"architecture_id":"A2","parent_id":"MISSING","mutation_id":"M2","fitness_delta":0.1}, persist=True)
    assert "parent_not_found" in refused["blocking_reasons"]
    assert refused["operation_applied"] is False
    assert history.read_bytes() == before
print("ACEE13_ORPHAN_BRANCH_OK")
