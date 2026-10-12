from __future__ import annotations
import subprocess,sys
from pathlib import Path
root=Path.home()/"open-cognitive-ecology"
required=(root/"acee6_k1_final_lock.py",root/"acee6_k_evidence"/"acee6_k1_property_report.json")
missing=[str(p) for p in required if not p.exists()]
if missing: raise SystemExit(f"k1_prerequisite_missing:{missing}")
r=subprocess.run([sys.executable,"acee6_k2_fast_acceptance_suite.py"],capture_output=True,text=True,timeout=180)
if r.stdout: print(r.stdout,end="")
if r.returncode: print(r.stderr,end="",file=sys.stderr); raise SystemExit(r.returncode)
print("ACEE6_K1_PREREQUISITES_PRESENT")
print("ACEE6_K2_FINAL_LOCK_OK")
