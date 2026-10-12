from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    root=Path(tmp); m=AceeLineageManager(root=root)
    m.step({"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"},persist=True)
    history=root/"acee_runtime/ACEE13_acee_lineage_manager/lineage_event_history.jsonl"
    history.write_text(history.read_text()+"{bad json\n")
    r=m.step({"operation":"inspect"},persist=False)
    assert not r["lineage_management_ready"] and r["history_corrupted"] is True
print("ACEE13_CORRUPTION_OK")
