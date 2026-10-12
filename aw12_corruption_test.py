import json, tempfile
from pathlib import Path
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
with tempfile.TemporaryDirectory() as d:
 e=EcologicalPredictionEngine(Path(d)); r=e.step(build_context(),True)
 Path(r["output_path"]).write_text("{corrupt")
 try: json.loads(Path(r["output_path"]).read_text())
 except json.JSONDecodeError: pass
 else: raise AssertionError("corruption not detectable")
 fresh=e.step(build_context(),False); assert fresh["prediction_status"]=="RF_ECOLOGY_PREDICTION_READY"
print("AW12_CORRUPTION_OK")
