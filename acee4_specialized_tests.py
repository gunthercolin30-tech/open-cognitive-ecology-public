from __future__ import annotations
import json, tempfile
from copy import deepcopy
from pathlib import Path
from acee4_fast_acceptance_suite import context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
with tempfile.TemporaryDirectory() as td:
 root=Path(td); e=AceeAutonomousCycleManager(root=root); a=e.step(inputs=context(),persist=False); b=e.step(inputs=deepcopy(context()),persist=False); assert a["cycle_hash"]==b["cycle_hash"]
 x=e.step(inputs=context(),persist=True); c=context(); c["cycle_id"]="cycle-002"; c["timestamp_utc"]="2026-07-13T20:01:00Z"; y=e.step(inputs=c,persist=True); assert y["previous_cycle_hash"]==x["cycle_hash"]
 records=[json.loads(z) for z in Path(y["history_path"]).read_text().splitlines() if z.strip()]; assert len(records)==2
 Path(y["history_path"]).write_text("{bad\n"); z=e.step(inputs=context(),persist=False); assert z["history_corrupted"] is True
print("ACEE4_SPECIALIZED_TESTS_OK")
