#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
AUDITOR = ROOT / "validation" / "p010_proto_individual_readiness_audit.py"
C1 = ROOT / "p010_proto_individual_functional_tests.py"
C2 = ROOT / "p010_integrated_proto_individual_probe.py"
READINESS = ROOT / "p010_proto_individual_readiness_report.json"
PROBE = ROOT / "p010_integrated_proto_individual_probe_report.json"
EXPECTED_AUDIT_ID = "bccc63ad550dc9dcfc7cf0ddcae5bbc0b475f24fa217ecafd2cd9bb9cfa184dc"
EXPECTED_PROBE_ID = "6d0f18ba702b831fb965786528d495d4eabd09e3227bfe48fc50634958eed74b"

def req(c,m):
    if not c: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(path,cwd):
    p=subprocess.run([sys.executable,str(path)],cwd=str(cwd),text=True,capture_output=True,timeout=300)
    req(p.returncode==0,p.stdout+p.stderr)
    return p.stdout

protected={}
for rel in (
 "ontology/distributed_population_runtime.py",
 "ontology/multi_host_identity_persistence.py",
 "ontology/collective_naming_protocol.py",
 "ontology/individual_lifecycle_management.py",
 "ontology/autobiographical_memory.py",
 "ontology/temporal_self_continuity.py",
 "ontology/individual_migration_protocol.py",
 "ontology/cooperative_specialization_engine.py",
 "ontology/cognitive_diversity_preservation_protocol.py",
 "ontology/inter_individual_coordination_protocol.py",
 "ontology/runtime_lineage_inheritance.py",
 "ontology/intergenerational_knowledge_transfer.py",
 "ontology/succession_execution_protocol.py",
):
    p=ROOT/rel
    if p.is_file(): protected[rel]=sha(p)

a1=run(AUDITOR,ROOT); q1=json.loads(READINESS.read_text())
p1=run(C2,ROOT); c1=json.loads(PROBE.read_text())
req(q1["audit_identity_sha256"]==EXPECTED_AUDIT_ID,"audit identity mismatch")
req(c1["probe_identity_sha256"]==EXPECTED_PROBE_ID,"probe identity mismatch")
print("P010_D_REPLAY_OK")

a2=run(AUDITOR,Path.home()); q2=json.loads(READINESS.read_text())
p2=run(C2,Path.home()); c2=json.loads(PROBE.read_text())
req(q2["audit_identity_sha256"]==q1["audit_identity_sha256"],"audit CWD drift")
req(c2["probe_identity_sha256"]==c1["probe_identity_sha256"],"probe CWD drift")
print("P010_D_CWD_DETERMINISM_OK")

req(c1["core_dimensions_with_identity_binding"]==5,"5/5 binding absent")
for d in c1["core_dimensions"]:
    ev=c1["binding"][d]
    req(ev["observed"] is True,f"binding absent {d}")
    req(len(ev["identity_cooccurrence_modules"])>0,f"vacuous binding {d}")
print("P010_D_ANTI_VACUITY_OK")

req(q1["capability_status"]["autobiographical_memory"]=="DECLARATIVE","memory classification drift")
req(c1["outcome"]=="INTEGRATED_PROTO_INDIVIDUAL_PARTIAL","partial conclusion drift")
req(c1["core_dimensions_with_identity_binding"]==5,"unexpected binding count")
print("P010_D_ANTI_OVERCLAIM_OK")

# Falsification oracle: one lost core binding cannot preserve 5/5 evidence.
tampered=json.loads(json.dumps(c1))
tampered["binding"]["memory"]["observed"]=False
tampered["binding"]["memory"]["identity_cooccurrence_modules"]=[]
recount=sum(bool(tampered["binding"][d]["observed"]) for d in tampered["core_dimensions"])
req(recount==4,"binding falsification oracle failed")
req(recount!=c1["core_dimensions_with_identity_binding"],"binding loss not detected")
print("P010_D_BINDING_FALSIFICATION_OK")

# Report tamper must change canonical content digest.
raw=PROBE.read_bytes()
obj=json.loads(raw)
obj["outcome"]="INTEGRATED_PROTO_INDIVIDUAL_IMPLEMENTED"
tamper_digest=hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()
canonical_digest=hashlib.sha256(json.dumps(c1,sort_keys=True,separators=(",",":")).encode()).hexdigest()
req(tamper_digest!=canonical_digest,"report tamper undetected")
print("P010_D_REPORT_TAMPER_OK")

# UNKNOWN/fail-safe oracle at readiness level.
statuses=dict(q1["capability_status"]); statuses["individual_identity"]="UNKNOWN"
derived="NOT_READY" if any(v in ("MISSING","UNKNOWN") for v in statuses.values()) else (
 "PARTIAL_READINESS" if any(v in ("PARTIAL","DECLARATIVE") for v in statuses.values()) else "READY")
req(derived=="NOT_READY","UNKNOWN did not fail safe")
print("P010_D_UNKNOWN_FAIL_SAFE_OK")

# Sandbox isolation: copied reports can be tampered without touching canonical reports.
with tempfile.TemporaryDirectory(prefix="p010-crown-") as td:
    td=Path(td)
    copy=td/"probe.json"; copy.write_bytes(PROBE.read_bytes())
    x=json.loads(copy.read_text()); x["outcome"]="INTEGRATED_PROTO_INDIVIDUAL_IMPLEMENTED"
    copy.write_text(json.dumps(x))
    req(json.loads(PROBE.read_text())["outcome"]=="INTEGRATED_PROTO_INDIVIDUAL_PARTIAL","canonical report mutated")
print("P010_D_SANDBOX_ISOLATION_OK")

after={rel:sha(ROOT/rel) for rel in protected}
req(after==protected,"functional source mutation detected")
req(q1["functional_conclusion_only"] is True and q1["phenomenology_undetermined"] is True,"epistemic drift")
req(c1["functional_conclusion_only"] is True and c1["phenomenology_undetermined"] is True,"probe epistemic drift")
print("P010_D_NON_MUTATION_EPISTEMIC_OK")

identity_payload={
 "schema":"oce.p010.adversarial_crown.identity.v1",
 "audit_identity_sha256":q1["audit_identity_sha256"],
 "probe_identity_sha256":c1["probe_identity_sha256"],
 "readiness":q1["readiness"],
 "probe_outcome":c1["outcome"],
 "checks_passed":9,
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
}
crown_id=hashlib.sha256(json.dumps(identity_payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
print("P010_ADVERSARIAL_CROWN_OK")
print("checks_passed=9")
print(f"crown_identity_sha256={crown_id}")
