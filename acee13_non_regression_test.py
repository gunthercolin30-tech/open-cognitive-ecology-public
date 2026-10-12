from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.acee_lineage_manager import AceeLineageManager
with TemporaryDirectory() as tmp:
    m=AceeLineageManager(root=Path(tmp)); d={"operation":"register_root","transaction_id":"T0","lineage_id":"L","architecture_id":"A0"}
    first=m.step(d,persist=True); second=m.step(d,persist=True)
    assert first["persisted"] is True and second["idempotent_replay"] is True
    assert len((Path(tmp)/"acee_runtime/ACEE13_acee_lineage_manager/lineage_event_history.jsonl").read_text().splitlines())==1
print("ACEE13_NON_REGRESSION_OK")
