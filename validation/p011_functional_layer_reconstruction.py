#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
A1_REPORT=ROOT/"p011_structural_dna_reconstruction_report.json"
REPORT=ROOT/"p011_functional_layer_reconstruction_report.json"
A1_ID="187d29b22ced7fc3dedd7876e2580a77a6ed0e6fed273d88e84be7bdac979f84"
ANCHORS={
"dna":"ontology/minimal_dna.py","anti_closure":"ontology/anti_closure_metaconstraint.py",
"future_openness":"ontology/future_openness.py","constitutional_continuity":"ontology/constitutional_continuity_validation.py",
"governance":"ontology/governance.py","approval":"ontology/governance_approval_policy_manager.py",
"amendment_gate":"ontology/external_governance_amendment_gate.py","self_improvement":"ontology/recursive_self_improvement_controller.py",
"evolution_sandbox":"ontology/evolution_sandbox.py","succession":"ontology/succession_execution_protocol.py",
"intergenerational":"ontology/intergenerational_knowledge_transfer.py","distributed_constitution":"ontology/distributed_constitutional_propagation.py",
"constitutional_memory":"ontology/distributed_constitutional_memory.py","runtime":"ontology/integrated_civilizational_runtime.py"}
CHAINS={
"dna_to_governance":["dna","governance","approval"],"governance_to_runtime":["governance","approval","runtime"],
"mutation_governance":["self_improvement","evolution_sandbox","approval","amendment_gate"],
"anti_closure_enforcement":["anti_closure","future_openness","governance","runtime"],
"constitutional_persistence":["constitutional_continuity","distributed_constitution","constitutional_memory"],
"succession_transmission":["succession","intergenerational","constitutional_memory"]}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def req(c,m):
    if not c: raise SystemExit("REFUSE: "+m)
req(A1_REPORT.is_file(),"A1 report missing")
a1=json.loads(A1_REPORT.read_text())
req(a1.get("audit_identity_sha256")==A1_ID,"A1 identity drift")
mods={}
for name,rel in ANCHORS.items():
    p=ROOT/rel
    info={"path":rel,"present":p.is_file(),"sha256":sha(p) if p.is_file() else None,"imports":[],"calls":[],"persistence_tokens":[],"enforcement_tokens":[]}
    if p.is_file():
        text=p.read_text(encoding="utf-8",errors="replace")
        try:
            tree=ast.parse(text)
            for n in ast.walk(tree):
                if isinstance(n,ast.Import): info["imports"] += [x.name for x in n.names]
                elif isinstance(n,ast.ImportFrom) and n.module: info["imports"].append(n.module)
                elif isinstance(n,ast.Call):
                    f=n.func
                    if isinstance(f,ast.Name): info["calls"].append(f.id)
                    elif isinstance(f,ast.Attribute): info["calls"].append(f.attr)
        except SyntaxError: pass
        low=text.lower()
        info["persistence_tokens"]=[x for x in ("json","persist","save","load","state","memory","ledger","registry","checkpoint") if x in low]
        info["enforcement_tokens"]=[x for x in ("reject","refuse","deny","rollback","validate","viable","approval","authorize","gate","enforce") if x in low]
    mods[name]=info
def mentions(a,b):
    if not mods[a]["present"] or not mods[b]["present"]: return False
    stem=Path(mods[b]["path"]).stem.lower()
    text=(ROOT/mods[a]["path"]).read_text(encoding="utf-8",errors="replace").lower()
    return stem in text or any(stem in x.lower() for x in mods[a]["imports"])
edges=[{"from":a,"to":b,"evidence":"STATIC_LINK"} for a in ANCHORS for b in ANCHORS if a!=b and mentions(a,b)]
chains={}
for cname,nodes in CHAINS.items():
    present=[n for n in nodes if mods[n]["present"]]
    direct=[]
    for a,b in zip(nodes,nodes[1:]):
        if mentions(a,b): direct.append(f"{a}->{b}")
        elif mentions(b,a): direct.append(f"{b}->{a}")
    status="UNKNOWN" if len(present)<len(nodes) else ("CALLABLE_LINK_SURFACE" if len(direct)>=len(nodes)-1 else ("STATIC_LINK_SURFACE" if direct else "COEXISTING_SURFACES"))
    chains[cname]={"status":status,"nodes":nodes,"present_nodes":present,"direct_relations":direct,
    "enforcement_surface_count":sum(bool(mods[n]["enforcement_tokens"]) for n in present),
    "persistence_surface_count":sum(bool(mods[n]["persistence_tokens"]) for n in present),
    "runtime_evidence":"UNKNOWN","persistent_end_to_end_evidence":"UNKNOWN"}
req(all(v["runtime_evidence"]=="UNKNOWN" for v in chains.values()),"runtime overclaim")
payload={"schema":"oce.p011.functional_layer_reconstruction.v1","milestone":"P011-B","status":"FUNCTIONAL_RELATIONS_PARTIAL",
"a1_audit_identity_sha256":A1_ID,"anchors":mods,"edges":edges,"chains":chains,
"epistemic_limits":["AST imports, calls and token surfaces establish structural/callable evidence only.","No end-to-end runtime enforcement is claimed.","Persistence tokens do not prove persistence of constitutional authority.","Conflict resolution and precedence require dynamic exercise."],
"functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["audit_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P011_FUNCTIONAL_LAYER_RECONSTRUCTION_OK")
print("status=FUNCTIONAL_RELATIONS_PARTIAL")
print(f"anchors_present={sum(x['present'] for x in mods.values())}/{len(mods)}")
print(f"static_edges={len(edges)}")
for k,v in chains.items(): print(f"{k}={v['status']} direct_relations={len(v['direct_relations'])}/{len(v['nodes'])-1} runtime=UNKNOWN persistence_e2e=UNKNOWN")
print(f"audit_identity_sha256={payload['audit_identity_sha256']}")
print(f"report={REPORT}")
