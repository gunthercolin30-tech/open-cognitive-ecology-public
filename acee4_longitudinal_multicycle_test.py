import json, tempfile
from copy import deepcopy
from pathlib import Path
from acee4_fast_acceptance_suite import context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
with tempfile.TemporaryDirectory() as td:
 e=AceeAutonomousCycleManager(root=Path(td)); prev=None
 for i in range(12):
  c=deepcopy(context()); c["cycle_id"]=f"long-{i}"; c["timestamp_utc"]=f"2026-07-13T22:{i:02d}:00Z"; r=e.step(inputs=c,persist=True); assert r["previous_cycle_hash"]==prev; prev=r["cycle_hash"]
 records=[json.loads(x) for x in Path(r["history_path"]).read_text().splitlines() if x.strip()]; assert len(records)==12
print("ACEE4_LONGITUDINAL_MULTICYCLE_OK")
