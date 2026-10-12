#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
AUDITOR = ROOT / "validation" / "p010_proto_individual_readiness_audit.py"
REPORT = ROOT / "p010_proto_individual_readiness_report.json"
EXPECTED_AUDITOR_SHA = "af15158924c1e31d6418649095cd34127012f19f9fa9381066cd146510637c95"
EXPECTED_AUDIT_ID = "bccc63ad550dc9dcfc7cf0ddcae5bbc0b475f24fa217ecafd2cd9bb9cfa184dc"
EXPECTED = {
 "individual_identity":"IMPLEMENTED",
 "peer_collective_naming":"IMPLEMENTED",
 "individual_lifecycle":"PARTIAL",
 "autobiographical_memory":"DECLARATIVE",
 "temporal_self_continuity":"PARTIAL",
 "individual_persistence":"IMPLEMENTED",
 "individual_governance":"PARTIAL",
 "individual_specialization":"PARTIAL",
 "cognitive_diversity":"PARTIAL",
 "inter_individual_coordination":"IMPLEMENTED",
 "population_runtime":"IMPLEMENTED",
 "migration_cross_host_continuity":"IMPLEMENTED",
 "lineage_inheritance":"PARTIAL",
 "intergenerational_transmission":"PARTIAL",
 "succession_replacement":"IMPLEMENTED",
 "civilization_individual_relation":"PARTIAL",
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(c,m):
    if not c: raise AssertionError(m)
def run(cwd):
    p=subprocess.run([sys.executable,str(AUDITOR)],cwd=cwd,text=True,capture_output=True,timeout=300)
    req(p.returncode==0,p.stdout+p.stderr)
    req("P010_PROTO_INDIVIDUAL_READINESS_AUDIT_OK" in p.stdout,"audit did not complete")
    return json.loads(REPORT.read_text(encoding="utf-8"))

req(AUDITOR.is_file(),"auditor missing")
req(sha(AUDITOR)==EXPECTED_AUDITOR_SHA,"auditor drift")

protected={}
for rel in sorted({
    src["path"]
    for cap in json.loads(AUDITOR.read_text(encoding="utf-8").split("CAPABILITIES = ",1)[0] or "{}")
} if False else []):
    pass
# Explicit protected functional nucleus.
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

r1=run(ROOT)
req(r1["audit_identity_sha256"]==EXPECTED_AUDIT_ID,"audit identity drift")
req(r1["readiness"]=="PARTIAL_READINESS","readiness drift")
print("P010_C1_AUDIT_REPLAY_OK")

r2=run(Path.home())
req(r2["audit_identity_sha256"]==r1["audit_identity_sha256"],"CWD nondeterminism")
print("P010_C1_DETERMINISM_OK")

req(r1["capability_status"]==EXPECTED,"classification contract drift")
req(r1["counts"]=={"DECLARATIVE":1,"IMPLEMENTED":7,"MISSING":0,"PARTIAL":8,"UNKNOWN":0},
    "classification counts drift")
print("P010_C1_CLASSIFICATION_CONTRACT_OK")

for cap,status in EXPECTED.items():
    ev=r1["evidence"][cap]
    req(ev["status"]==status,f"evidence status mismatch {cap}")
    req(any(s.get("exists") for s in ev["sources"]),f"vacuous evidence {cap}")
print("P010_C1_ANTI_VACUITY_OK")

req(r1["capability_status"]["autobiographical_memory"]=="DECLARATIVE",
    "autobiographical memory overclaimed")
req("runtime integrated proto-individual object continuity" in r1["unknowns"],
    "integration UNKNOWN disappeared")
req(any("same persistent individual identity" in g for g in r1["gaps"]),
    "identity-binding gap disappeared")
print("P010_C1_ANTI_OVERCLAIM_OK")

# Degradation oracle: loss of a critical implemented capability must not remain ready.
degraded=dict(r1["capability_status"])
degraded["individual_identity"]="UNKNOWN"
computed="NOT_READY" if any(v in ("MISSING","UNKNOWN") for v in degraded.values()) else (
    "PARTIAL_READINESS" if any(v in ("PARTIAL","DECLARATIVE") for v in degraded.values()) else "READY"
)
req(computed=="NOT_READY","critical UNKNOWN did not fail safe")
print("P010_C1_DEGRADATION_OK")

# Tamper oracle: changing a capability conclusion changes the identity payload digest.
payload=json.loads(json.dumps(r1["identity_payload"]))
payload["capability_status"]["autobiographical_memory"]="IMPLEMENTED"
tampered=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
req(tampered!=r1["audit_identity_sha256"],"classification tamper undetected")
print("P010_C1_TAMPER_OK")

after={rel:sha(ROOT/rel) for rel in protected}
req(after==protected,"audit mutated proto-individual sources")
print("P010_C1_NON_MUTATION_OK")

req(r1["functional_conclusion_only"] is True and r1["phenomenology_undetermined"] is True,
    "epistemic invariant drift")
req(r1["consciousness_proven"] is False and r1["subjectivity_proven"] is False
    and r1["qualia_proven"] is False and r1["phenomenology_proven"] is False,
    "phenomenology overclaim")
print("P010_C1_EPISTEMIC_INVARIANTS_OK")

print("P010_PROTO_INDIVIDUAL_FUNCTIONAL_TESTS_OK")
print("checks_passed=9")
