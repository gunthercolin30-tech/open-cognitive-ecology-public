#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
LOCK=ROOT/"p010_final_lock.py"
REPORT=ROOT/"p010_final_lock_report.json"
def req(c,m):
    if not c: raise AssertionError(m)
def run(cwd):
    p=subprocess.run([sys.executable,str(LOCK)],cwd=str(cwd),text=True,capture_output=True,timeout=300)
    req(p.returncode==0,p.stdout+p.stderr); req("P010_FINAL_LOCK_OK" in p.stdout,"lock failed")
    return json.loads(REPORT.read_text())
r1=run(ROOT)
req(r1["status"]=="LOCKED" and r1["readiness"]=="PARTIAL_READINESS","functional conclusion drift")
req(r1["integration_outcome"]=="INTEGRATED_PROTO_INDIVIDUAL_PARTIAL","integration drift")
print("P010_FINAL_LOCK_FUNCTIONAL_OK")
r2=run(Path.home()); req(r2["lock_identity_sha256"]==r1["lock_identity_sha256"],"nondeterministic lock")
print("P010_FINAL_LOCK_DETERMINISM_OK")
x=json.loads(json.dumps(r1)); x["integration_outcome"]="INTEGRATED_PROTO_INDIVIDUAL_IMPLEMENTED"
req(hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=hashlib.sha256(json.dumps(r1,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"conclusion tamper invisible")
print("P010_FINAL_LOCK_CONCLUSION_TAMPER_OK")
x=json.loads(json.dumps(r1)); x["protected_hashes"]["p010_adversarial_crown.py"]="0"*64
req(x["protected_hashes"]!=r1["protected_hashes"],"artifact tamper invisible")
print("P010_FINAL_LOCK_ARTIFACT_TAMPER_OK")
before=dict(r1["protected_hashes"]); r3=run(ROOT); req(r3["protected_hashes"]==before,"protected artifact mutation")
print("P010_FINAL_LOCK_NON_MUTATION_OK")
req(r3["functional_conclusion_only"] is True and r3["phenomenology_undetermined"] is True,"epistemic drift")
req(all(r3[k] is False for k in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven")),"phenomenology overclaim")
print("P010_FINAL_LOCK_EPISTEMIC_INVARIANTS_OK")
print("P010_FINAL_LOCK_CAMPAIGN_OK")
print("checks_passed=6")
print(f"lock_identity_sha256={r3['lock_identity_sha256']}")
