from __future__ import annotations
import subprocess,sys
for test in ("acee6_k0_final_lock.py","acee6_k1_fast_acceptance_suite.py"):
    r=subprocess.run([sys.executable,test],capture_output=True,text=True,timeout=300)
    if r.stdout: print(r.stdout,end="")
    if r.returncode: print(r.stderr,end="",file=sys.stderr); raise SystemExit(r.returncode)
print("ACEE6_K1_FINAL_LOCK_OK")
