#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
B_REPORT=ROOT/"p011_functional_layer_reconstruction_report.json"
REPORT=ROOT/"p011_c0_executable_interface_report.json"
B_ID="2dbd735a034110a3c125bd4f9430d26165d1f3d437a8a812a3fe4ed9fb4b7419"

ANCHORS={
"dna":"ontology/minimal_dna.py",
"anti_closure":"ontology/anti_closure_metaconstraint.py",
"future_openness":"ontology/future_openness.py",
"constitutional_continuity":"ontology/constitutional_continuity_validation.py",
"governance":"ontology/governance.py",
"approval":"ontology/governance_approval_policy_manager.py",
"amendment_gate":"ontology/external_governance_amendment_gate.py",
"self_improvement":"ontology/recursive_self_improvement_controller.py",
"evolution_sandbox":"ontology/evolution_sandbox.py",
"succession":"ontology/succession_execution_protocol.py",
"intergenerational":"ontology/intergenerational_knowledge_transfer.py",
"distributed_constitution":"ontology/distributed_constitutional_propagation.py",
"constitutional_memory":"ontology/distributed_constitutional_memory.py",
"runtime":"ontology/integrated_civilizational_runtime.py",
}
ACTION_WORDS=("validate","check","approve","reject","deny","authorize","execute","apply","mutate","revise","update","commit","rollback","persist","save","load","restore","propagate","transfer","succeed","replace","enforce","viable","evaluate")

def req(c,m):
    if not c: raise SystemExit("REFUSE: "+m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
req(B_REPORT.is_file(),"P011-B report missing")
b=json.loads(B_REPORT.read_text())
req(b.get("audit_identity_sha256")==B_ID,"P011-B identity drift")

result={}
for name,rel in ANCHORS.items():
    p=ROOT/rel
    req(p.is_file(),f"anchor missing: {rel}")
    text=p.read_text(encoding="utf-8",errors="replace")
    tree=ast.parse(text)
    classes=[]
    funcs=[]
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            args=[a.arg for a in node.args.args]
            funcs.append({"name":node.name,"args":args,"async":isinstance(node,ast.AsyncFunctionDef),
                          "action_like":any(w in node.name.lower() for w in ACTION_WORDS)})
        elif isinstance(node,ast.ClassDef):
            methods=[]
            for m in node.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    args=[a.arg for a in m.args.args if a.arg!="self"]
                    methods.append({"name":m.name,"args":args,"async":isinstance(m,ast.AsyncFunctionDef),
                                    "action_like":any(w in m.name.lower() for w in ACTION_WORDS)})
            classes.append({"name":node.name,"methods":methods})
    actionable=[f["name"] for f in funcs if f["action_like"]]
    for c in classes:
        actionable += [c["name"]+"."+m["name"] for m in c["methods"] if m["action_like"]]
    result[name]={"path":rel,"sha256":sha(p),"functions":funcs,"classes":classes,
                  "actionable_interfaces":sorted(actionable),
                  "actionable_count":len(actionable)}

runtime_candidates=[k for k,v in result.items() if v["actionable_count"]>0]
payload={
"schema":"oce.p011.c0.executable_interface_audit.v1",
"milestone":"P011-C0",
"status":"EXECUTABLE_INTERFACES_MAPPED",
"p011_b_identity_sha256":B_ID,
"anchors":result,
"anchors_with_actionable_interfaces":runtime_candidates,
"actionable_anchor_count":len(runtime_candidates),
"epistemic_limits":[
"Callable signatures are not evidence that the calls are wired into the civilizational runtime.",
"Constructors are not executed by this audit.",
"No persistent state is modified.",
"Dynamic P011-C1 tests must use only interfaces established here or explicit dependencies discovered from them."
],
"functional_conclusion_only":True,"phenomenology_undetermined":True,
"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["audit_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P011_C0_EXECUTABLE_INTERFACE_AUDIT_OK")
print("status=EXECUTABLE_INTERFACES_MAPPED")
print(f"anchors={len(result)}/{len(ANCHORS)}")
print(f"actionable_anchors={len(runtime_candidates)}/{len(ANCHORS)}")
for k in ANCHORS:
    print(f"{k}=actionable:{result[k]['actionable_count']}")
print(f"audit_identity_sha256={payload['audit_identity_sha256']}")
print(f"report={REPORT}")
