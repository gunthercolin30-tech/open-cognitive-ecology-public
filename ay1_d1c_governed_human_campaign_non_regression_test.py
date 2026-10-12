import hashlib,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;ps=[R/"ontology/governed_relation_review_gate.py",R/"ontology/validated_relation_registry.py",R/"fast_acceptance.py"];b={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in ps};q=subprocess.run([sys.executable,str(R/"run_ay1_d1c_governed_human_review.py"),"status"],cwd=R,capture_output=True);assert q.returncode==0;assert b=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in ps};print("AY1_D1C_GOVERNED_HUMAN_CAMPAIGN_NON_REGRESSION_OK")
