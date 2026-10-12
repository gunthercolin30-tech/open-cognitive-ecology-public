#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"p012_a2_component_segmentation_report.json"

FAMILIES={
"world_model_prediction":("world","predict","forecast","counterfactual","transition","state_model","planning"),
"individual_identity_memory":("individual","identity","autobiograph","personal_memory","naming","lifecycle","specialization"),
"governance_structural_dna":("governance","constitution","dna","constraint","anti_closure","openness","succession","amendment"),
"capability_discovery_evolution":("capability","discovery","evolution","mutation","self_improvement","architecture_genealogy"),
"scientific_validation_evidence":("validation","experiment","replication","scientific","evidence","statistics","theorem","certif"),
"coordination_collective":("coordination","collective","consensus","distributed","federat","multi_agent","population"),
"interface_human_review":("interface","dashboard","nicegui","human_review","dialogue","renderer","oif"),
"external_world_tools":("web","navigation","external","browser","api","connector","sensor","multimodal"),
"economic_resource_efficiency":("economic","cost","resource","efficiency","budget","quota","market","product"),
"memory_continuity_archive":("memory","archive","history","continuity","checkpoint","lineage","intergenerational"),
"runtime_operations":("runtime","scheduler","orchestrator","execution","action","transaction","rollback","monitor"),
}

EXCLUDE_PREFIXES=(".git/",".venv/","venv/","__pycache__/")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git_files():
    try:
        raw=subprocess.check_output(["git","-C",str(ROOT),"ls-files","-z","--","*.py"])
        return [x.decode() for x in raw.split(b"\0") if x]
    except Exception:
        return [str(p.relative_to(ROOT)) for p in ROOT.rglob("*.py")]

def score_family(text):
    t=text.lower()
    scores={k:sum(1 for w in ws if w in t) for k,ws in FAMILIES.items()}
    best=max(scores.values(),default=0)
    return sorted(k for k,v in scores.items() if v==best and v>0),scores

inventory=ROOT/"ontology_inventory.txt"
if not inventory.is_file(): raise SystemExit("P012_A2_REFUSED: ontology_inventory.txt missing")
inv_before=sha(inventory)

rows=[]; parse_errors=[]; fam_counts=Counter(); evidence_counts=Counter()
for rel in sorted(set(git_files())):
    if rel.startswith(EXCLUDE_PREFIXES) or rel.endswith(".py.bak") or "/__pycache__/" in rel: continue
    p=ROOT/rel
    if not p.is_file(): continue
    try: text=p.read_text(errors="replace")
    except Exception: continue
    try:
        tree=ast.parse(text,filename=rel)
        classes=[n.name for n in ast.walk(tree) if isinstance(n,ast.ClassDef)]
        funcs=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
        imports=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import): imports += [a.name for a in n.names]
            elif isinstance(n,ast.ImportFrom) and n.module: imports.append(n.module)
    except SyntaxError as e:
        parse_errors.append({"path":rel,"line":e.lineno,"message":e.msg})
        classes=[]; funcs=[]; imports=[]
    lexical=" ".join([rel]+classes+funcs+imports)
    families,scores=score_family(lexical)
    if not families: families=["unclassified"]
    for f in families: fam_counts[f]+=1
    evidence=[]
    low=rel.lower()
    if low.startswith("validation/") or "test" in low: evidence.append("VALIDATION_OR_TEST_SURFACE")
    if "report" in low or "audit" in low: evidence.append("REPORT_OR_AUDIT_SURFACE")
    if classes or funcs: evidence.append("EXECUTABLE_API_SURFACE")
    if any(x in low for x in ("dashboard","interface","nicegui","renderer")): evidence.append("USER_INTERFACE_SURFACE")
    if any(x in low for x in ("external","web","api","connector")): evidence.append("EXTERNAL_INTEGRATION_SURFACE")
    if not evidence: evidence=["SOURCE_ONLY"]
    for e in evidence: evidence_counts[e]+=1
    rows.append({"path":rel,"sha256":sha(p),"families":families,
                 "family_scores":{k:v for k,v in scores.items() if v},
                 "class_count":len(classes),"function_count":len(funcs),
                 "evidence_surfaces":evidence})

# Cross-family product-oriented segmentation, without claiming customer value yet.
product_candidates=[]
for r in rows:
    if r["families"]!=["unclassified"] and (
       "USER_INTERFACE_SURFACE" in r["evidence_surfaces"] or
       "EXTERNAL_INTEGRATION_SURFACE" in r["evidence_surfaces"] or
       "EXECUTABLE_API_SURFACE" in r["evidence_surfaces"]):
        product_candidates.append(r["path"])

payload={
"schema":"oce.p012.a2.component_segmentation.v1",
"milestone":"P012-A2",
"status":"COMPONENT_SEGMENTATION_COMPLETE",
"method":"deterministic lexical+AST segmentation of tracked Python sources; product relevance/customer value not inferred",
"ontology_inventory_sha256":inv_before,
"python_source_count":len(rows),
"parse_error_count":len(parse_errors),
"parse_errors":parse_errors,
"family_counts":dict(sorted(fam_counts.items())),
"evidence_surface_counts":dict(sorted(evidence_counts.items())),
"product_surface_candidate_count":len(product_candidates),
"product_surface_candidates":product_candidates,
"components":rows,
"limits":[
"Family membership is heuristic segmentation, not proof of runtime use.",
"Product-surface candidacy is not evidence of customer demand, willingness to pay, or product-market fit.",
"Multiple families may tie for one component.",
"Unclassified components remain explicit rather than being forced into a category."
],
"functional_conclusion_only":True,"phenomenology_undetermined":True,
"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
payload["segmentation_identity_sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
if sha(inventory)!=inv_before: raise SystemExit("P012_A2_REFUSED: ontology_inventory mutated during audit")
OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
print("P012_A2_COMPONENT_SEGMENTATION_OK")
print(f"python_source_count={len(rows)}")
print(f"parse_error_count={len(parse_errors)}")
print(f"families={len(fam_counts)}")
print(f"product_surface_candidate_count={len(product_candidates)}")
print("ontology_inventory_non_mutation=OK")
print("segmentation_identity_sha256="+payload["segmentation_identity_sha256"])
print("report="+str(OUT))
