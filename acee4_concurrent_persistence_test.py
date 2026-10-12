from concurrent.futures import ThreadPoolExecutor
import json, tempfile
from copy import deepcopy
from pathlib import Path
from acee4_fast_acceptance_suite import context
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager
with tempfile.TemporaryDirectory() as td:
 root=Path(td)
 def run(i):
  c=deepcopy(context()); c["cycle_id"]=f"cycle-{i}"; c["timestamp_utc"]=f"2026-07-13T21:{i:02d}:00Z"; return AceeAutonomousCycleManager(root=root).step(inputs=c,persist=True)
 with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,range(8)))
 records=[json.loads(x) for x in Path(results[0]["history_path"]).read_text().splitlines() if x.strip()]
 assert len(records)==8 and len({x["cycle_id"] for x in records})==8
 for i in range(1,len(records)): assert records[i]["previous_cycle_hash"]==records[i-1]["cycle_hash"]
print("ACEE4_CONCURRENT_PERSISTENCE_OK")
