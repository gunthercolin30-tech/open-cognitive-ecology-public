from pathlib import Path
import ast,json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
CAND=ROOT/"validation_artifacts/p159/occ1k_r9/governed_semantic_binding_candidate_set_v1.json"
R9D=ROOT/"validation_artifacts/p159/occ1k_r9d/superseding_source_rebind_transaction_receipt_v1.json"
R9E=ROOT/"validation_artifacts/p159/occ1k_r9e/post_rebind_independent_replay_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9f"
SOURCES={"P156_CCAD":"ontology/ccad_specification.py","P091_CONSTITUTION_OPERATIONAL":"ontology/constitution_operational.py",
"CONSTITUTION_REGISTRY":"ontology/constitution_registry.py","NORMATIVE_HIERARCHY":"ontology/normative_hierarchy.py",
"GOVERNANCE_CONTEXTUAL":"ontology/governance_contextual.py"}
EXPECTED={"S7-C1":("P156_CCAD","CONFLICT_CLASSES"),"S7-C2":("P156_CCAD","PRINCIPLES"),
"S7-C3":("NORMATIVE_HIERARCHY","lower_may_not_contradict_higher"),"S8-C1":("P091_CONSTITUTION_OPERATIONAL","DNA_OPERATIONAL_BRIDGES"),
"S8-C2":("CONSTITUTION_REGISTRY","_CONSTITUTION_RULES"),"S8-C3":("NORMATIVE_HIERARCHY","CANONICAL_LEVEL_GROUPS"),
"S10-C1":("P091_CONSTITUTION_OPERATIONAL","REQUIRED_EVIDENCE_FIELDS"),"S10-C2":("GOVERNANCE_CONTEXTUAL","CONFLICT")}
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def names(path):
 t=ast.parse(path.read_text(encoding="utf-8")); out=set()
 for n in ast.walk(t):
  if isinstance(n,(ast.Assign,ast.AnnAssign)):
   ts=n.targets if isinstance(n,ast.Assign) else [n.target]
   for q in ts:
    if isinstance(q,ast.Name):out.add(q.id)
  if isinstance(n,ast.Name):out.add(n.id)
  # Exact mapping keys are structural semantic anchors too.
  if isinstance(n,ast.Dict):
   for k in n.keys:
    if isinstance(k,ast.Constant) and isinstance(k.value,str):out.add(k.value)
  # Exact literal return values can be semantic status anchors.
  # Restrict this to dictionary values returned by executable code;
  # do not accept arbitrary prose/docstring occurrences.
  if isinstance(n,ast.Return) and isinstance(n.value,ast.Dict):
   for v in n.value.values:
    if isinstance(v,ast.Constant) and isinstance(v.value,str):out.add(v.value)
 return out
def build():
 c=json.loads(CAND.read_text()); d=json.loads(R9D.read_text()); e=json.loads(R9E.read_text())
 if d.get("status")!="COMMITTED" or d.get("decision")!="REBIND_CURRENT":raise RuntimeError("R9D_NOT_COMMITTED")
 if e.get("status")!="POST_REBIND_REPLAY_COMPLETE" or e["conclusion"].get("fl_b3")!="BLOCKED":raise RuntimeError("R9E_STATE_UNEXPECTED")
 flat={x["candidate_id"]:x for rows in c["candidates"].values() for x in rows}
 checks={}; proposals=[]
 for cid,(sid,anchor) in EXPECTED.items():
  x=flat.get(cid); p=ROOT/SOURCES[sid]; ns=names(p)
  ok=bool(x and x.get("source_id")==sid and x.get("semantic_anchor")==anchor and anchor in ns)
  checks[cid]=ok
  if not ok:raise RuntimeError("SEMANTIC_ANCHOR_NOT_VERIFIED:"+cid)
  proposals.append({"candidate_id":cid,"target_phase":next(k for k,v in c["candidates"].items() if x in v),
    "source_id":sid,"source_path":SOURCES[sid],"source_sha256":sha(p),"semantic_anchor":anchor,
    "kind":x["kind"],"proposed_status":"GOVERNED_SOURCE_BACKED_BINDING",
    "normative_effect":True,"runtime_authority_granted":False,"execution_performed":False})
 r={"schema":"oce.p159.occ1k.r9f.governed_semantic_binding_adoption_dossier.v1","milestone":"P159/OCC-1K-R9F",
 "status":"HUMAN_GOVERNED_ADOPTION_DECISION_REQUIRED","candidate_count":len(proposals),"anchor_checks":checks,
 "proposals":proposals,"decision":{"adopt":None,"explicit_confirmation_required":True,
 "confirmation_token":"I_CONFIRM_R9F_GOVERNED_SEMANTIC_BINDING_ADOPTION",
 "meaning":"Adopt exactly these eight source-backed semantic bindings as a superseding OCC-1A relational binding layer; no runtime authority or execution is created."},
 "epistemic_boundaries":{"s7_pass_claimed":False,"s8_pass_claimed":False,"s10_runtime_enforcement_claimed":False,
 "fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,"p160b_opened":False},
 "mutation":{"canonical_sources_modified":False,"candidate_set_modified":False,"adoption_performed":False,
 "runtime_binding_created":False,"execution_performed":False},
 "next_if_confirmed":"R9G_ATOMIC_GOVERNED_SEMANTIC_BINDING_COMMIT",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
 r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest();return r
def write():
 OUT.mkdir(parents=True,exist_ok=True);r=build();p=OUT/"governed_semantic_binding_adoption_dossier_v1.json";p.write_bytes(canon(r)+b"\n");return r,p
def main():
 r,p=write();print("P159_OCC1K_R9F_GOVERNED_SEMANTIC_BINDING_ADOPTION_DOSSIER_COMPLETE")
 print("STATUS="+r["status"]);print("CANDIDATES=8/8");print("ANCHORS_VERIFIED=8/8")
 print("ADOPTION_PERFORMED=false");print("RUNTIME_BINDING_CREATED=false");print("EXECUTION_PERFORMED=false")
 print("FL_B3=BLOCKED");print("LOCK_READY=false");print("LOCK_GRANTED=false");print("P160B_OPENED=false")
 print("NEXT="+r["next_if_confirmed"]);print("ARTIFACT_SHA256="+sha(p))
if __name__=="__main__":main()
