import json,subprocess,sys
from pathlib import Path
R=Path.home()/"open-cognitive-ecology"
subprocess.run([sys.executable,"acee6_k2_final_lock.py"],cwd=R,check=True,timeout=240)
subprocess.run([sys.executable,"acee6_k3_fast_acceptance_suite.py"],cwd=R,check=True,timeout=240)
p=R/"acee6_k_evidence"/"acee6_k3_mutation_report.json"; assert p.is_file(); d=json.loads(p.read_text()); assert d["threshold_met"] and d["mutation_score"]>=0.95
print("ACEE6_K3_FINAL_LOCK_OK")
