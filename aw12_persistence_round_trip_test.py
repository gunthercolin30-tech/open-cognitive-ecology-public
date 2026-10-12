import json, tempfile
from pathlib import Path
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
with tempfile.TemporaryDirectory() as d:
 e=EcologicalPredictionEngine(Path(d)); r=e.step(build_context(),True)
 loaded=json.loads(Path(r["output_path"]).read_text())
 assert loaded["prediction_hash"]==r["prediction_hash"]
 lines=Path(r["history_path"]).read_text().splitlines(); assert len(lines)==1
 e.step(build_context(),True); assert len(Path(r["history_path"]).read_text().splitlines())==2
print("AW12_PERSISTENCE_ROUND_TRIP_OK")
