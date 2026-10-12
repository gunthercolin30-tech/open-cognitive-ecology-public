from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    manager = AceeLineageManager(root=root)
    manager.step(inputs={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}, persist=True)
    history = root / "acee_runtime" / "ACEE13_acee_lineage_manager" / "lineage_event_history.jsonl"
    prefix = history.read_bytes()
    manager.step(inputs={"operation":"register_candidate","transaction_id":"T1","lineage_id":"L","generation_id":1,"architecture_id":"A1","parent_id":"A0","mutation_id":"M1","fitness_delta":0.1}, persist=True)
    after = history.read_bytes()
    assert after.startswith(prefix)
    assert len(after) > len(prefix)
print("ACEE13_APPEND_ONLY_HISTORY_OK")
