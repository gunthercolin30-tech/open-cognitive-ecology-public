#!/usr/bin/env python3
from pathlib import Path
import copy, json, subprocess, sys
from ontology.p160_final_lock import verify_lock, invalidate_lock, sha256_file

ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p160/p160k"
MAN=OUT/"final_lock_manifest.json"
REPORT=OUT/"final_lock_report.json"
if not MAN.is_file() or not REPORT.is_file(): raise SystemExit("P160K_ARTIFACTS_MISSING")
m=json.loads(MAN.read_text(encoding="utf-8"))
expected_lock="6177f3ad633fa1659e1c7f78b1d2dec2215cfe75b6a4a9666665fa3742e40ee1"
if m.get("lock_hash")!=expected_lock: raise SystemExit("LOCK_IDENTITY_DRIFT")
current={rel:(sha256_file(ROOT/rel) if (ROOT/rel).is_file() else "MISSING") for rel in m["protected_hashes"]}
checks={}
checks["baseline_verify"]=verify_lock(m,current)["valid"]
bad=dict(current); first=next(iter(bad)); bad[first]="0"*64
checks["protected_drift_rejected"]=not verify_lock(m,bad)["valid"]
tam=copy.deepcopy(m); tam["scope"]={"tampered":True}
checks["manifest_tamper_rejected"]=not verify_lock(tam,current)["valid"]
inv=invalidate_lock(m,"terminal-crown-controlled-test")
checks["explicit_invalidation_terminal"]=(inv["status"]=="LOCK_INVALIDATED" and not verify_lock(inv,current)["valid"])
sov=copy.deepcopy(m); sov["invariants"]["authorization_created"]=True
checks["authorization_inflation_rejected"]=not verify_lock(sov,current)["valid"]
p161=copy.deepcopy(m); p161["invariants"]["p161_opened"]=True
checks["p161_premature_open_rejected"]=not verify_lock(p161,current)["valid"]
candidate=None
for rel in sorted(m["evidence_hashes"]):
    q=ROOT/rel
    if q.is_file() and "p160k" not in rel.lower():
        candidate=q; break
if candidate is None: raise SystemExit("NO_SAFE_EVIDENCE_CANDIDATE")
original=candidate.read_bytes()
try:
    candidate.write_bytes(original+b"\nP160K_CONTROLLED_DRIFT\n")
    cp=subprocess.run([sys.executable,"-m","validation.p160k_final_lock_independent_verifier"],cwd=ROOT,text=True,capture_output=True)
    checks["independent_evidence_drift_rejected"]=(cp.returncode!=0 and "EVIDENCE_DRIFT:" in (cp.stdout+cp.stderr))
finally:
    candidate.write_bytes(original)
checks["evidence_restored_exact"]=(sha256_file(candidate)==m["evidence_hashes"][str(candidate.relative_to(ROOT))])
cp=subprocess.run([sys.executable,"-m","validation.p160k_final_lock_independent_verifier"],cwd=ROOT,text=True,capture_output=True)
checks["post_restore_independent_verify"]=(cp.returncode==0 and "P160K_INDEPENDENT_FINAL_LOCK_VERIFIED" in cp.stdout)
r=json.loads(REPORT.read_text(encoding="utf-8"))
checks["report_non_sovereign"]=(r.get("authorization_created") is False and r.get("execution_performed") is False and r.get("P161_OPENED") is False)
failed=[k for k,v in checks.items() if not v]
result={"schema":"oce.p160.terminal_crown.v1","milestone":"P160-K","lock_hash":m["lock_hash"],"checks":checks,"passed":not failed,"failed":failed,"P161_OPENED":False}
(OUT/"terminal_crown_report.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
for k,v in checks.items(): print(("PASS " if v else "FAIL ")+k)
if failed: raise SystemExit("P160K_TERMINAL_CROWN_FAILED:"+",".join(failed))
print("P160K_TERMINAL_CROWN_OK")
print("CHECKS=%d/%d"%(len(checks),len(checks)))
print("LOCK_HASH="+m["lock_hash"])
print("P161_OPENED=false")
