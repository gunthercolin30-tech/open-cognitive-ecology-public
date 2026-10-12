#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "p009_final_lock_report.json"
EXPECTED = {
    "validation/p009_wm_readiness_audit.py": "44f5f8525e22c80f4f7652b878ebc46d2774eef493149d2758f7f245411e04aa",
    "p009_wm_functional_tests.py": "0805fb37bf00b539b0ca81a4a2b7f06281a58bf8673977de23e34f594c349e23",
    "p009_wm_closed_loop_probe.py": "06c6fb47ced950e628c158ab672bf7cb8a75bdb9e03cd14cc0d8e36938ce1524",
    "p009_adversarial_crown.py": "0b4d8789aa5757baae179a54b9d89e1872fa21c1f54bffd90bdfe72efeea0a08",
}
EXPECTED_AUDIT_ID = "2f680a8f70f27596f090fc0a064477a906c586704f5dfbc17b4f92eaee5af05e"
EXPECTED_CROWN_ID = "e6bc7681f23967884624010da28c2bf4e490ddda5963c6de106acae690ccaf55"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(c,m):
    if not c: raise AssertionError(m)
def run(rel):
    p=subprocess.run([sys.executable,str(ROOT/rel)],cwd=ROOT,text=True,capture_output=True,timeout=300)
    req(p.returncode==0,p.stdout+p.stderr)
    return p.stdout+p.stderr

for rel,h in EXPECTED.items():
    p=ROOT/rel; req(p.is_file(),f"missing {rel}"); req(sha(p)==h,f"drift {rel}")

a=run("validation/p009_wm_readiness_audit.py")
req("P009_WM_READINESS_AUDIT_OK" in a,"audit replay failed")
f=run("p009_wm_functional_tests.py")
req("P009_WM_FUNCTIONAL_TESTS_OK" in f,"functional replay failed")
p=run("p009_wm_closed_loop_probe.py")
req("outcome=CLOSED_LOOP_PARTIAL" in p,"probe conclusion drift")
c=run("p009_adversarial_crown.py")
req("P009_ADVERSARIAL_CROWN_OK" in c,"crown replay failed")

audit=json.loads((ROOT/"p009_wm_readiness_report.json").read_text())
probe=json.loads((ROOT/"p009_wm_closed_loop_probe_report.json").read_text())
crown=json.loads((ROOT/"p009_adversarial_crown_report.json").read_text())

req(audit["audit_identity_sha256"]==EXPECTED_AUDIT_ID,"audit identity drift")
req(audit["readiness"]=="PARTIAL_READINESS","readiness conclusion drift")
req(probe["outcome"]=="CLOSED_LOOP_PARTIAL","closed-loop conclusion drift")
req(crown["crown_identity_sha256"]==EXPECTED_CROWN_ID,"crown identity drift")
req(crown["checks_passed"]==9 and crown["status"]=="PASSED","crown status drift")

payload={
 "schema":"oce.p009.final_lock.identity.v1",
 "milestone":"P009",
 "status":"LOCKED",
 "prerequisite_sha256":EXPECTED,
 "audit_identity_sha256":EXPECTED_AUDIT_ID,
 "crown_identity_sha256":EXPECTED_CROWN_ID,
 "wm_readiness":"PARTIAL_READINESS",
 "runtime_closed_loop":"CLOSED_LOOP_PARTIAL",
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
report={
 "schema":"oce.p009.final_lock.v1",
 "milestone":"P009",
 "status":"LOCKED",
 "lock_identity_sha256":identity,
 "identity_payload":payload,
 "wm_readiness":"PARTIAL_READINESS",
 "runtime_closed_loop":"CLOSED_LOOP_PARTIAL",
 "audit_identity_sha256":EXPECTED_AUDIT_ID,
 "crown_identity_sha256":EXPECTED_CROWN_ID,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
 "consciousness_proven":False,
 "subjectivity_proven":False,
 "qualia_proven":False,
 "phenomenology_proven":False,
}
REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P009_FINAL_LOCK_OK")
print("status=LOCKED")
print("wm_readiness=PARTIAL_READINESS")
print("runtime_closed_loop=CLOSED_LOOP_PARTIAL")
print(f"lock_identity_sha256={identity}")
print(f"report={REPORT}")
