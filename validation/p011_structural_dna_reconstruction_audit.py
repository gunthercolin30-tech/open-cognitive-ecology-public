#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, re, subprocess
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "p011_structural_dna_reconstruction_report.json"

LAYERS = {
"L0_declarative_constraints": ("constraint","rule","policy","norm","invariant"),
"L1_executable_invariants": ("invariant","validate","viability","compliance","integrity"),
"L2_identity_continuity": ("identity","continuity","lineage","narrative_identity"),
"L3_governance_authorization": ("governance","approval","authorization","permission","revocation"),
"L4_governed_mutation_revision": ("mutation","self_improvement","revision","evolution_sandbox","amendment"),
"L5_inheritance_transmission_succession": ("inherit","transmission","intergenerational","succession","lineage"),
"L6_anti_closure_future_openness": ("anti_closure","non_closure","future_openness","closure_pressure","openness"),
"L7_civilizational_constitution": ("constitution","constitutional","civilizational","society"),
"L8_runtime_enforcement": ("runtime","dispatcher","gate","supervisor","controller","execution"),
}
ANCHORS = {
"minimal_dna":"ontology/minimal_dna.py",
"anti_closure":"ontology/anti_closure_metaconstraint.py",
"future_openness":"ontology/future_openness.py",
"constitutional_continuity":"ontology/constitutional_continuity_validation.py",
"governance":"ontology/governance.py",
"governance_approval":"ontology/governance_approval_policy_manager.py",
"external_amendment_gate":"ontology/external_governance_amendment_gate.py",
"self_improvement_controller":"ontology/recursive_self_improvement_controller.py",
"evolution_sandbox":"ontology/evolution_sandbox.py",
"succession_execution":"ontology/succession_execution_protocol.py",
"intergenerational_transfer":"ontology/intergenerational_knowledge_transfer.py",
"distributed_constitution":"ontology/distributed_constitutional_propagation.py",
"constitutional_memory":"ontology/distributed_constitutional_memory.py",
"runtime":"ontology/integrated_civilizational_runtime.py",
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tracked():
    try:
        p=subprocess.run(["git","ls-files"],cwd=ROOT,text=True,capture_output=True,timeout=30)
        if p.returncode==0:
            return [ROOT/x for x in p.stdout.splitlines() if x.endswith(".py") and (ROOT/x).is_file()]
    except Exception: pass
    return list((ROOT/"ontology").glob("*.py"))+list((ROOT/"validation").glob("*.py"))

inventory=ROOT/"ontology_inventory.txt"
if not inventory.is_file(): raise SystemExit("REFUSE: ontology_inventory.txt missing")
files=tracked()
records=[]
parse_errors=[]
for p in files:
    try: text=p.read_text(encoding="utf-8",errors="replace")
    except Exception: continue
    try: ast.parse(text)
    except SyntaxError as e:
        parse_errors.append({"path":str(p.relative_to(ROOT)),"line":e.lineno,"message":e.msg})
    low=(str(p.relative_to(ROOT))+"\n"+text).lower()
    layer_hits={k:sum(low.count(t) for t in toks) for k,toks in LAYERS.items()}
    if any(layer_hits.values()):
        records.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p),"layer_hits":layer_hits})

layer_summary={}
for layer in LAYERS:
    hits=[r for r in records if r["layer_hits"][layer]>0]
    strong=[r for r in hits if r["layer_hits"][layer]>=3]
    layer_summary[layer]={
        "candidate_count":len(hits),
        "strong_candidate_count":len(strong),
        "examples":[r["path"] for r in sorted(strong,key=lambda x:(-x["layer_hits"][layer],x["path"]))[:12]],
        "status":"IMPLEMENTED_SURFACES" if strong else ("DECLARATIVE_SURFACES" if hits else "UNKNOWN"),
    }

anchors={}
for name,rel in ANCHORS.items():
    p=ROOT/rel
    anchors[name]={"path":rel,"present":p.is_file(),"sha256":sha(p) if p.is_file() else None}

# Explicitly inspect Minimal DNA contract without claiming system-wide enforcement.
dna=ROOT/"ontology/minimal_dna.py"
dna_contract={"present":dna.is_file(),"dependencies":[],"has_invariants":False,"has_mutable_traits":False,"has_viability_check":False}
if dna.is_file():
    t=dna.read_text(encoding="utf-8",errors="replace")
    m=re.search(r"DEPENDENCIES\s*=\s*\[(.*?)\]",t,re.S)
    if m: dna_contract["dependencies"]=re.findall(r'["\']([^"\']+)["\']',m.group(1))
    dna_contract["has_invariants"]="_invariants" in t
    dna_contract["has_mutable_traits"]="_mutable_traits" in t
    dna_contract["has_viability_check"]="is_viable" in t

status="PARTIAL_RECONSTRUCTION"
if not dna_contract["present"]: status="STRUCTURAL_DNA_ANCHOR_MISSING"

payload={
 "schema":"oce.p011.structural_dna_reconstruction.v1",
 "milestone":"P011-A1",
 "status":status,
 "inventory_sha256":sha(inventory),
 "python_source_count":len(files),
 "relevant_source_count":len(records),
 "parse_error_count":len(parse_errors),
 "parse_errors":parse_errors[:20],
 "minimal_dna_contract":dna_contract,
 "anchors":anchors,
 "layers":layer_summary,
 "epistemic_limits":[
   "Static reconstruction does not prove end-to-end runtime enforcement.",
   "Token/symbol presence does not prove constitutional authority or precedence.",
   "A module named governance/constitution/DNA is not by itself evidence of active enforcement.",
   "Cross-layer ordering, conflict resolution, persistence and mutation protection require dedicated functional probes."
 ],
 "functional_conclusion_only":True,
 "phenomenology_undetermined":True,
 "consciousness_proven":False,
 "subjectivity_proven":False,
 "qualia_proven":False,
 "phenomenology_proven":False,
}
identity_payload={k:v for k,v in payload.items() if k not in ("parse_errors",)}
payload["audit_identity_sha256"]=hashlib.sha256(json.dumps(identity_payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
REPORT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P011_STRUCTURAL_DNA_RECONSTRUCTION_AUDIT_OK")
print(f"status={status}")
print(f"python_source_count={len(files)}")
print(f"relevant_source_count={len(records)}")
print(f"parse_error_count={len(parse_errors)}")
for layer in LAYERS:
    x=layer_summary[layer]
    print(f"{layer}={x['status']} candidates={x['candidate_count']} strong={x['strong_candidate_count']}")
print(f"audit_identity_sha256={payload['audit_identity_sha256']}")
print(f"report={REPORT}")
