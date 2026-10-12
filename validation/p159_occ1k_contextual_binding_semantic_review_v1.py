from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
U=ROOT/"validation_artifacts/p159/occ1k_r9u/subgroup_consumer_source_evidence_resolution_v1.json"
W=ROOT/"validation_artifacts/p159/occ1k_r9w/governed_direct_rule_consumer_binding_layer_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9x/contextual_binding_semantic_review_v1.json"
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 u=load(U);w=load(W); rows=[]
 adopted={b["rule_id"] for b in w["bindings"]}
 for x in u["subgroups"]:
  if x["evidence_strength"]=="DIRECT_SEMANTIC_ROLE_MATCH":continue
  strength=x["evidence_strength"]
  rows.append({"subgroup_id":x["subgroup_id"],"rule_ids":x["rule_ids"],
   "source_object_id":x.get("source_object_id"),"evidence_ids":x.get("evidence_ids",[]),
   "prior_evidence_strength":strength,"candidate_consumers":x.get("candidate_consumers",[]),
   "review_result":"REQUIRES_EXPLICIT_SOURCE_OR_GOVERNED_SEMANTIC_BINDING" if strength.startswith("CONTEXTUAL") else "UNRESOLVED",
   "binding_adopted":False})
 assert not adopted.intersection({r for x in rows for r in x["rule_ids"]})
 contextual=sum(x["prior_evidence_strength"].startswith("CONTEXTUAL") for x in rows)
 unresolved=sum(x["prior_evidence_strength"]=="UNRESOLVED" for x in rows)
 return {"schema":"oce.p159.occ1k.r9x.contextual.binding.semantic.review.v1","milestone":"P159/OCC-1K-R9X",
 "status":"RESIDUAL_SEMANTIC_REVIEW_COMPLETE_GOVERNED_BINDING_EVIDENCE_REQUIRED",
 "inputs":{"r9u_sha256":sha(U),"r9w_binding_layer_sha256":sha(W)},
 "residual_subgroups":rows,"counts":{"residual_subgroups":len(rows),"contextual":contextual,"unresolved":unresolved,
 "new_bindings_adopted":0},
 "conclusion":{"contextual_candidate_is_not_binding_evidence":True,"r9w_direct_bindings_not_reused_as_precedent":True,
 "keyword_mapping_forbidden":True,"residual_binding_requires_explicit_source_or_governed_semantic_decision":True},
 "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"runtime_binding_created":False,
 "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
 "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
 "next_required_step":"R9Y_GOVERNED_RESIDUAL_SEMANTIC_BINDING_DOSSIER",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9X_CONTEXTUAL_BINDING_SEMANTIC_REVIEW_COMPLETE")
 print("STATUS="+d["status"]);print("RESIDUAL_SUBGROUPS=%d/15"%c["residual_subgroups"])
 print("CONTEXTUAL=%d/14"%c["contextual"]);print("UNRESOLVED=%d/1"%c["unresolved"])
 print("NEW_BINDINGS_ADOPTED=0");print("R9W_DIRECT_BINDINGS_REUSED_AS_PRECEDENT=false")
 print("KEYWORD_MAPPING=false");print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("NEXT="+d["next_required_step"])
 print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
