import hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
paths=[R/"run_ay1_d1c_governed_human_review.py",R/"ontology/governed_relation_review_gate.py",R/"ontology/validated_relation_registry.py"]
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
import run_ay1_d1c_governed_human_review_ui
assert before=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
print("AY1_D1C_GOVERNED_HUMAN_REVIEW_UI_NON_REGRESSION_OK")
