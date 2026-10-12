#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
REPORT=ROOT/"p010_final_lock_report.json"
AUDIT=ROOT/"p010_proto_individual_readiness_report.json"
PROBE=ROOT/"p010_integrated_proto_individual_probe_report.json"
CROWN=ROOT/"p010_adversarial_crown.py"
EXPECTED={
 "validation/p010_proto_individual_readiness_audit.py":"af15158924c1e31d6418649095cd34127012f19f9fa9381066cd146510637c95",
 "p010_proto_individual_functional_tests.py":"c5ca3c9f92abfb3bbf72c95ec76522d2a72dce63a3a58169e62b62c54e9ad1f0",
 "p010_integrated_proto_individual_probe.py":"c6513c03855f8a2fa431312f4bdf4523b64a222d947473bf5bf0e92db0c6ab7c",
 "p010_adversarial_crown.py":"56a0e577eabeac023ea4d8ab293587b416bcda28f670f81199c795bea1d6a2af",
}
AUDIT_ID="bccc63ad550dc9dcfc7cf0ddcae5bbc0b475f24fa217ecafd2cd9bb9cfa184dc"
PROBE_ID="6d0f18ba702b831fb965786528d495d4eabd09e3227bfe48fc50634958eed74b"
CROWN_ID="7bf378e97618077c76d26e0bdbe898c451569dcd600a2e5ad04a07567ada4494"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(c,m):
    if not c: raise SystemExit("REFUSE: "+m)
for rel,h in EXPECTED.items():
    p=ROOT/rel; req(p.is_file(),f"missing {rel}"); req(sha(p)==h,f"drift {rel}")
req(AUDIT.is_file(),"readiness report missing"); req(PROBE.is_file(),"probe report missing")
a=json.loads(AUDIT.read_text()); p=json.loads(PROBE.read_text())
req(a["audit_identity_sha256"]==AUDIT_ID,"audit identity drift")
req(p["probe_identity_sha256"]==PROBE_ID,"probe identity drift")
req(a["readiness"]=="PARTIAL_READINESS","readiness conclusion drift")
req(p["outcome"]=="INTEGRATED_PROTO_INDIVIDUAL_PARTIAL","integration conclusion drift")
req(a["capability_status"]["autobiographical_memory"]=="DECLARATIVE","memory overclaim")
req(p["core_dimensions_with_identity_binding"]==5,"binding frontier drift")
cp=subprocess.run([sys.executable,str(CROWN)],cwd=str(ROOT),text=True,capture_output=True,timeout=300)
req(cp.returncode==0,cp.stdout+cp.stderr)
req("P010_ADVERSARIAL_CROWN_OK" in cp.stdout,"crown replay failed")
req(f"crown_identity_sha256={CROWN_ID}" in cp.stdout,"crown identity drift")
protected={rel:sha(ROOT/rel) for rel in EXPECTED}
payload={
 "schema":"oce.p010.final_lock.identity.v1",
 "milestone":"P010",
 "status":"LOCKED",
 "readiness":"PARTIAL_READINESS",
 "integration_outcome":"INTEGRATED_PROTO_INDIVIDUAL_PARTIAL",
 "core_identity_binding":"5/5",
 "autobiographical_memory":"DECLARATIVE",
 "audit_identity_sha256":AUDIT_ID,
 "probe_identity_sha256":PROBE_ID,
 "crown_identity_sha256":CROWN_ID,
 "protected_hashes":protected,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
lock_id=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
report=dict(payload)
report.update({
 "schema":"oce.p010.final_lock.v1",
 "lock_identity_sha256":lock_id,
 "consciousness_proven":False,"subjectivity_proven":False,
 "qualia_proven":False,"phenomenology_proven":False,
})
REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P010_FINAL_LOCK_OK")
print("status=LOCKED")
print("readiness=PARTIAL_READINESS")
print("integration_outcome=INTEGRATED_PROTO_INDIVIDUAL_PARTIAL")
print("core_identity_binding=5/5")
print("autobiographical_memory=DECLARATIVE")
print(f"lock_identity_sha256={lock_id}")
print(f"report={REPORT}")
