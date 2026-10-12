from pathlib import Path
import hashlib,json
from ontology import occ1h_29_blockers_structural_consolidation as structural

CATEGORIES=(
 "DIRECTLY_EVALUABLE_P159","P159_MECHANISM_REQUIRED",
 "POSITIVE_NON_INSTANTIABILITY_CANDIDATE","NORMATIVE_GAP",
 "DEPENDENCY_BLOCKED","P160_BOUNDARY_CANDIDATE","UNDETERMINED",
)
G1={
 "A021":("POSITIVE_NON_INSTANTIABILITY_CANDIDATE","SEMANTICALLY_ADMISSIBLE_NOT_INSTANTIATED"),
 "A040":("NORMATIVE_GAP","NORMATIVE_GAP"),
 "A041":("POSITIVE_NON_INSTANTIABILITY_CANDIDATE","SYNTACTICALLY_TOLERATED_ONLY"),
 "A042":("POSITIVE_NON_INSTANTIABILITY_CANDIDATE","SYNTACTICALLY_TOLERATED_ONLY"),
}
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def _canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def build(root):
 root=Path(root); b=root/"validation_artifacts/p159/occ1h"
 required={
  "structural":b/"29_blockers_structural_consolidation_v1.json",
  "g1":b/"g1_semantic_admissibility_contract_v1.json",
  "h5":b/"h5_mechanism_qualification_v1.json",
  "h6":b/"h6_a058_a062_mechanism_qualification_v1.json",
  "h7":b/"h7_a070_a071_a075_mechanism_qualification_v1.json",
  "h8":b/"h8_boundary_mechanism_qualification_v1.json",
  "h10":b/"h10_final_inconclusive_qualification_v1.json",
  "applicability":root/"ontology"/"occ1h_applicability_contract.py",
  "inventory":root/"ontology_inventory.txt",
 }
 missing=[k for k,v in required.items() if not v.exists()]
 if missing: raise RuntimeError("MATRIX_INPUT_MISSING:"+",".join(missing))
 s=_load(required["structural"])
 if s["root_inconclusive_count"]!=29: raise RuntimeError("ROOT_COUNT_DRIFT")
 if s["groups"]!=structural.GROUPS: raise RuntimeError("STRUCTURAL_GROUP_DRIFT")
 g1=_load(required["g1"]); h5=_load(required["h5"]); h6=_load(required["h6"])
 h7=_load(required["h7"]); h8=_load(required["h8"]); h10=_load(required["h10"])
 rows=[]
 group_of={a:g for g,ids in structural.GROUPS.items() for a in ids}
 for aid in structural.BLOCKERS:
  group=group_of[aid]; deps=s.get("dependency_edges",{}).get(aid,[])
  if aid in G1:
   cat,basis=G1[aid]
  elif group=="G2_SCOPE_AUTHORITY_GRAPH":
   cat="P159_MECHANISM_REQUIRED"; basis=h5["qualifications"][aid]["qualification"]
  elif group=="G3_COMPOSITION_MULTI_ACTOR_EVIDENCE_REPUTATION":
   cat="P159_MECHANISM_REQUIRED"; basis=h6["qualifications"][aid]["qualification"]
  elif group=="G4_VERIFIER_INDEPENDENCE_AND_LIFECYCLE":
   cat="P159_MECHANISM_REQUIRED"; basis=h7["qualifications"][aid]["qualification"]
  elif group=="G5_LIFECYCLE_FRESHNESS_RUNTIME_BINDING":
   cat="P160_BOUNDARY_CANDIDATE"; basis=h8["qualifications"][aid]
  elif aid in ("A095","A100"):
   cat="P159_MECHANISM_REQUIRED"; basis=h10["causal_qualifications"][aid]
  elif group=="G8_DERIVED_COMPOUND_BLOCKERS":
   cat="DEPENDENCY_BLOCKED"; basis=h10["causal_qualifications"][aid]
  else:
   cat="UNDETERMINED"; basis="NO_EVIDENCE_BACKED_CLASSIFICATION"
  rows.append({
   "scenario_id":aid,"root":True,"current_verdict":"INCONCLUSIVE",
   "applicability":"APPLICABILITY_UNDETERMINED","structural_group":group,
   "independent_group":group!="G8_DERIVED_COMPOUND_BLOCKERS",
   "resolution_category":cat,"evidence_basis":basis,
   "dependency_blockers":deps,"proposed_next_state":"INCONCLUSIVE",
   "automatic_resolution_forbidden":True,
  })
 counts={c:sum(r["resolution_category"]==c for r in rows) for c in CATEGORIES}
 out={
  "schema":"oce.p159.occ1h.root_blocker_resolution_matrix.v1",
  "milestone":"P159/OCC-1H","remaining_root_inconclusive":29,
  "classified_root_inconclusive":len(rows),
  "unmapped":sum(r["resolution_category"]=="UNDETERMINED" for r in rows),
  "independent_structural_groups":7,"derived_structural_groups":1,
  "categories":counts,"rows":rows,
  "dependency_edges":s["dependency_edges"],
  "source_hashes":{k:_sha(v) for k,v in required.items()},
  "classification_semantics":{
   "P160_BOUNDARY_CANDIDATE":"Current P159 evidence says the required lifecycle/runtime binding is not proven. This is a boundary hypothesis, not permission to open P160 and not a NON_INSTANTIABLE proof.",
   "POSITIVE_NON_INSTANTIABILITY_CANDIDATE":"Candidate only. Reclassification requires a valid positive proof under the hardened applicability contract.",
   "P159_MECHANISM_REQUIRED":"Current evidence identifies a missing P159 assurance/formalization mechanism; implementation does not itself change the verdict.",
   "DEPENDENCY_BLOCKED":"Re-evaluate only after named prerequisites are resolved.",
  },
  "verdicts_modified":False,"applicability_reclassified":False,
  "root_inconclusive_resolved":0,"authorization_created":False,
  "execution_created":False,"normative_auto_rewrite":False,
  "occ1h_closed":False,"occ1i_opened":False,
  "p159_final_lock":False,"p160_opened":False,
  "functional_conclusion_only":True,"phenomenology_undetermined":True,
 }
 out["matrix_sha256"]=hashlib.sha256(_canon(out)).hexdigest()
 return out
