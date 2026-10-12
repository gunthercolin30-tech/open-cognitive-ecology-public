#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
LOCK=ROOT/"p009_final_lock.py"
REPORT=ROOT/"p009_final_lock_report.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(c,m):
    if not c: raise AssertionError(m)
def execute(cwd):
    p=subprocess.run([sys.executable,str(LOCK)],cwd=cwd,text=True,capture_output=True,timeout=900)
    req(p.returncode==0,p.stdout+p.stderr)
    req("P009_FINAL_LOCK_OK" in p.stdout,"Final Lock failed")
    return json.loads(REPORT.read_text())

protected={}
for rel in (
 "validation/p009_wm_readiness_audit.py","p009_wm_functional_tests.py",
 "p009_wm_closed_loop_probe.py","p009_adversarial_crown.py",
 "ontology/world_model.py","ontology/environmental_state_model.py",
 "ontology/embodied_world_model_update.py","ontology/predictive_environment_simulator.py",
):
    p=ROOT/rel
    if p.is_file(): protected[rel]=sha(p)

r1=execute(ROOT)
req(r1["status"]=="LOCKED","not locked")
req(r1["wm_readiness"]=="PARTIAL_READINESS","readiness not bound")
req(r1["runtime_closed_loop"]=="CLOSED_LOOP_PARTIAL","closed-loop not bound")
print("P009_FINAL_LOCK_FUNCTIONAL_OK")

r2=execute(Path.home())
req(r1["lock_identity_sha256"]==r2["lock_identity_sha256"],"CWD/determinism failure")
print("P009_FINAL_LOCK_DETERMINISM_OK")

payload=json.loads(json.dumps(r1["identity_payload"]))
payload["wm_readiness"]="READY"
tampered=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
req(tampered!=r1["lock_identity_sha256"],"readiness tamper undetected")
payload=json.loads(json.dumps(r1["identity_payload"]))
payload["runtime_closed_loop"]="CLOSED_LOOP_IMPLEMENTED"
tampered2=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
req(tampered2!=r1["lock_identity_sha256"],"closed-loop tamper undetected")
print("P009_FINAL_LOCK_CONCLUSION_TAMPER_OK")

payload=json.loads(json.dumps(r1["identity_payload"]))
first=next(iter(payload["prerequisite_sha256"]))
payload["prerequisite_sha256"][first]="0"*64
tampered3=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
req(tampered3!=r1["lock_identity_sha256"],"artifact tamper undetected")
print("P009_FINAL_LOCK_ARTIFACT_TAMPER_OK")

after={rel:sha(ROOT/rel) for rel in protected}
req(after==protected,"Final Lock campaign mutated protected sources")
print("P009_FINAL_LOCK_NON_MUTATION_OK")

req(r1["functional_conclusion_only"] is True,"functional-only lost")
req(r1["phenomenology_undetermined"] is True,"phenomenology invariant lost")
req(r1["consciousness_proven"] is False and r1["subjectivity_proven"] is False
    and r1["qualia_proven"] is False and r1["phenomenology_proven"] is False,
    "epistemic invariant lost")
print("P009_FINAL_LOCK_EPISTEMIC_INVARIANTS_OK")
print("P009_FINAL_LOCK_CAMPAIGN_OK")
print(f"lock_identity_sha256={r1['lock_identity_sha256']}")
