#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from ontology.governance_approval_policy_manager import GovernanceApprovalPolicyManager
from ontology.evolution_sandbox import EvolutionSandbox
from ontology.distributed_constitutional_memory import DistributedConstitutionalMemory

C1_REPORT=ROOT/"p011_c1_dynamic_enforcement_probe_report.json"
REPORT=ROOT/"p011_c2_persistence_restart_probe_report.json"
C1_ID="8f41c83843218c5b5b89e7b146ef0e21ea618e4d5802d1e98b21654ae46f0832"

def req(c,m):
    if not c: raise AssertionError(m)

def tree_digest(root):
    h=hashlib.sha256()
    for p in sorted((root/"ontology").glob("*.py")):
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()

req(C1_REPORT.is_file(),"C1 report missing")
req(json.loads(C1_REPORT.read_text()).get("probe_identity_sha256")==C1_ID,"C1 identity drift")
before=tree_digest(ROOT)
tests={}
observations={}

with tempfile.TemporaryDirectory(prefix="p011-c2-") as td:
    sandbox=Path(td)
    (sandbox/"ontology_inventory.txt").write_text("",encoding="utf-8")

    pm1=GovernanceApprovalPolicyManager()
    pm1.set_policy("p011_restart_probe","disabled")
    first=pm1.evaluate_action("p011_restart_probe")
    pm2=GovernanceApprovalPolicyManager()
    second=pm2.evaluate_action("p011_restart_probe")
    tests["governance_policy_restart_contract"]=first["status"]=="blocked" and second["status"]!="blocked"
    observations["governance_policy_restart"]="INSTANCE_LOCAL_OBSERVED"

    es1=EvolutionSandbox(root=sandbox)
    good=es1.simulate({"mutation_id":"persist-good"},{"baseline_score":0.80,"projected_score":0.90,"reversibility_score":1.0,"non_closure_score":1.0,"constitutional_score":1.0,"validation_score":1.0,"regression_risk":0.0,"closure_pressure_delta":0.0})
    es2=EvolutionSandbox(root=sandbox)
    bad=es2.simulate({"mutation_id":"persist-bad"},{"baseline_score":0.90,"projected_score":0.95,"reversibility_score":1.0,"non_closure_score":1.0,"constitutional_score":1.0,"validation_score":1.0,"regression_risk":0.0,"closure_pressure_delta":0.2})
    tests["evolution_sandbox_restart_enforcement"]=good["sandbox_approved"] is True and bad["sandbox_approved"] is False and bad["sandbox_rollback_required"] is True
    observations["evolution_sandbox_restart"]="PROTECTION_REINSTANTIATED_OBSERVED"

    cm1=DistributedConstitutionalMemory()
    state1=cm1.step({"constitutional_state":{"version":"p011-c2","non_closure":True},"source_node":"node-a"})
    cm2=DistributedConstitutionalMemory()
    state2=cm2.step({"constitutional_state":{"version":"p011-c2","non_closure":True},"source_node":"node-a"})
    s1=json.dumps(state1,sort_keys=True,default=str)
    s2=json.dumps(state2,sort_keys=True,default=str)
    tests["constitutional_memory_restart_callable"]=bool(state1) and bool(state2)
    observations["constitutional_memory_restart"]="REINSTANTIATION_OBSERVED"
    observations["constitutional_memory_state_equivalence"]="OBSERVED" if s1==s2 else "NOT_IDENTICAL"

after=tree_digest(ROOT)
tests["active_ontology_non_mutation"]=before==after
failed=[k for k,v in tests.items() if not v]
req(not failed,"failed tests: "+",".join(failed))

payload={
"schema":"oce.p011.c2.persistence_restart_probe.v1",
"milestone":"P011-C2",
"status":"PERSISTENCE_RESTART_PARTIAL",
"c1_probe_identity_sha256":C1_ID,
"tests":tests,
"checks_passed":sum(tests.values()),
"checks_total":len(tests),
"observations":observations,
"conclusion":{
"protection_reinstantiation":"OBSERVED",
"instance_local_policy_non_persistence":"OBSERVED",
"constitutional_memory_reinstantiation":"OBSERVED",
"end_to_end_constitutional_state_persistence":"UNKNOWN"
},
"limits":[
"Reinstantiation of protective behavior is not equivalent to persistence of a single civilizational constitutional state.",
"GovernanceApprovalPolicyManager policy mutation is observed as instance-local under this probe; this is not classified as a defect without a persistence contract.",
"Distributed constitutional memory is exercised across fresh instances, but this probe does not claim cross-host durability or authoritative precedence.",
"Succession and intergenerational transmission are reserved for P011-C3."
],
"functional_conclusion_only":True,"phenomenology_undetermined":True,
"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["probe_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
for k in tests:
    print("P011_C2_"+k.upper()+"_OK")
print("P011_C2_PERSISTENCE_RESTART_PROBE_OK")
print(f"checks_passed={sum(tests.values())}/{len(tests)}")
print("protection_reinstantiation=OBSERVED")
print("end_to_end_constitutional_state_persistence=UNKNOWN")
print(f"probe_identity_sha256={payload['probe_identity_sha256']}")
print(f"report={REPORT}")
