#!/usr/bin/env python3
from __future__ import annotations
import ast, copy, hashlib, json
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
P013C=ROOT/"p013_c_governed_v1_v2_mapping_matrix_report.json"
P013E=ROOT/"p013_e_final_lock_report.json"
P014A=ROOT/"p014_a_legacy_capability_boundary_contract_report.json"
INV=ROOT/"ontology_inventory.txt"
OUT=ROOT/"p014_b_governed_legacy_candidate_assessment_report.json"

EXPECTED_P013E="15e9aa6993266c7a6c01993da0d285f48ad2c1719fbde560679c3d10edff9e72"
EXPECTED_P014A="6698bee8229a108f290f3797b6f34e94c28040a365900dba81c98268885adae4"

def fail(x): raise SystemExit("P014_B_REFUSED: "+x)
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

for p in (P013C,P013E,P014A,INV):
    if not p.is_file(): fail("missing prerequisite: "+str(p))
inv0=sha(INV)
c,e,a=load(P013C),load(P013E),load(P014A)
if e.get("final_lock_identity_sha256")!=EXPECTED_P013E: fail("P013-E identity drift")
if a.get("contract_identity_sha256")!=EXPECTED_P014A: fail("P014-A identity drift")
rows=c.get("rows",[])
if len(rows)!=2095: fail("P013-C population drift")
keep=[r for r in rows if r.get("migration_decision")=="KEEP"]
unk=[r for r in rows if r.get("migration_decision")=="UNKNOWN"]
if len(keep)!=973 or len(unk)!=1122: fail("P013-C decision boundary drift")

def path_of(r):
    for k in ("path","source_path","module_path","file"):
        v=r.get(k)
        if isinstance(v,str) and v: return v
    return None

def static_evidence(p):
    raw=p.read_bytes()
    tree=ast.parse(raw.decode("utf-8"),filename=str(p))
    funcs=[]; classes=[]
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            funcs.append({"name":n.name,"async":isinstance(n,ast.AsyncFunctionDef),
                          "required_positional":max(0,len(n.args.posonlyargs)+len(n.args.args)-len(n.args.defaults)),
                          "has_vararg":n.args.vararg is not None,"has_kwarg":n.args.kwarg is not None})
        elif isinstance(n,ast.ClassDef):
            methods=[m.name for m in n.body if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and not m.name.startswith("__")]
            classes.append({"name":n.name,"public_methods":sorted(methods)})
    imports=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.Import):
            imports += [x.name for x in n.names]
        elif isinstance(n,ast.ImportFrom) and n.module:
            imports.append(n.module)
    return {
      "source_sha256":hashlib.sha256(raw).hexdigest(),
      "parse_status":"OK",
      "top_level_callable_count":len(funcs)+len(classes),
      "top_level_functions":sorted(funcs,key=lambda x:x["name"]),
      "top_level_classes":sorted(classes,key=lambda x:x["name"]),
      "imports":sorted(set(imports)),
    }

assess=[]
for r in sorted(keep,key=lambda x:path_of(x) or ""):
    rel=path_of(r)
    if not rel: fail("KEEP row without source path")
    p=ROOT/rel
    if not p.is_file(): fail("missing KEEP source: "+rel)
    try: ev=static_evidence(p)
    except Exception as ex: fail(f"KEEP source parse failure {rel}: {type(ex).__name__}: {ex}")
    # P014-B is deliberately conservative: static source evidence alone cannot prove
    # target-contract runtime compatibility or incompatibility.
    assess.append({
      "component":rel,
      "p013_decision":"KEEP",
      "source_sha256":ev["source_sha256"],
      "static_evidence":ev,
      "target_contract_evidence":"ABSENT_IN_P014_B_STATIC_ASSESSMENT",
      "runtime_evidence":"NOT_EXECUTED",
      "compatibility_status":"UNKNOWN",
      "reason":"Static structural evidence is insufficient to prove V2 target-contract runtime compatibility or incompatibility.",
      "risk":"UNTESTED_RUNTIME_BOUNDARY",
      "evidence_provenance":["P013-C KEEP decision","P014-A boundary contract","static AST/source inspection"],
    })

tests=[]
def t(n,v): tests.append({"name":n,"passed":bool(v)})
t("coverage_973",len(assess)==973)
t("all_p013_keep",all(x["p013_decision"]=="KEEP" for x in assess))
t("all_sources_sha256",all(len(x["source_sha256"])==64 for x in assess))
t("all_parse_ok",all(x["static_evidence"]["parse_status"]=="OK" for x in assess))
t("static_only_preserves_unknown",all(x["compatibility_status"]=="UNKNOWN" for x in assess))
t("no_runtime_execution",all(x["runtime_evidence"]=="NOT_EXECUTED" for x in assess))
t("no_false_incompatible",not any(x["compatibility_status"]=="INCOMPATIBLE" for x in assess))
t("no_false_compatible",not any(x["compatibility_status"]=="COMPATIBLE" for x in assess))
t("p013e_binding",e.get("final_lock_identity_sha256")==EXPECTED_P013E)
t("p014a_binding",a.get("contract_identity_sha256")==EXPECTED_P014A)
t("p013_population_preserved",len(rows)==2095)
t("p013_unknown_preserved",len(unk)==1122)
t("unique_candidate_paths",len({x["component"] for x in assess})==973)
t("ontology_nonmutation_prewrite",sha(INV)==inv0)

if not all(x["passed"] for x in tests): fail("self-test failure")

report={
 "schema":"oce.p014.governed_legacy_candidate_assessment.v1",
 "milestone":"P014-B",
 "status":"VALIDATED",
 "policy":{
   "population":"P013-C KEEP only",
   "keep_implies_runtime_compatible":False,
   "static_evidence_can_prove_runtime_compatibility":False,
   "absence_of_runtime_evidence_implies_incompatible":False,
   "unknown_preservation":True,
   "runtime_execution_performed":False,
 },
 "summary":{
   "candidate_count":973,
   "assessed_count":len(assess),
   "COMPATIBLE":sum(x["compatibility_status"]=="COMPATIBLE" for x in assess),
   "INCOMPATIBLE":sum(x["compatibility_status"]=="INCOMPATIBLE" for x in assess),
   "UNKNOWN":sum(x["compatibility_status"]=="UNKNOWN" for x in assess),
 },
 "assessments":assess,
 "tests":{"passed":sum(x["passed"] for x in tests),"total":len(tests),"details":tests},
 "bindings":{
   "p013_c_report_sha256":sha(P013C),
   "p013_e_final_lock_identity_sha256":EXPECTED_P013E,
   "p014_a_contract_identity_sha256":EXPECTED_P014A,
   "ontology_inventory_sha256":inv0,
 },
 "epistemic_status":{
   "functional_conclusion_only":True,"phenomenology_undetermined":True,
   "consciousness_proven":False,"subjectivity_proven":False,
   "qualia_proven":False,"phenomenology_proven":False
 },
 "next_step":"P014-C adapter core or a governed runtime compatibility campaign, without promoting UNKNOWN from static evidence alone."
}
report["assessment_identity_sha256"]=stable(report)
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
if sha(INV)!=inv0: fail("ontology inventory mutated")
rt=load(OUT); ident=rt.pop("assessment_identity_sha256")
if stable(rt)!=ident: fail("round-trip identity failure")

print("P014_B_GOVERNED_LEGACY_CANDIDATE_ASSESSMENT_OK")
print("status=VALIDATED")
print(f"tests={len(tests)}/{len(tests)}")
print("candidates=973")
print("assessed=973/973")
print("COMPATIBLE=0")
print("INCOMPATIBLE=0")
print("UNKNOWN=973")
print("runtime_execution=NONE")
print("static_evidence_promotes_compatibility=NO")
print("p013_e_binding=VERIFIED")
print("p014_a_binding=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("assessment_identity_sha256="+ident)
print("report="+str(OUT))
