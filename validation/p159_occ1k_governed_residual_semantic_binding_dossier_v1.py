from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
X=ROOT/"validation_artifacts/p159/occ1k_r9x/contextual_binding_semantic_review_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9y/governed_residual_semantic_binding_dossier_v1.json"
def load(): return json.loads(X.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 x=load(); contextual=[]; unresolved=[]
 for r in x["residual_subgroups"]:
  item={"subgroup_id":r["subgroup_id"],"rule_ids":r["rule_ids"],"source_object_id":r.get("source_object_id"),
        "evidence_ids":r.get("evidence_ids",[]),"candidate_consumers":r.get("candidate_consumers",[]),
        "prior_evidence_strength":r["prior_evidence_strength"],"binding_adopted":False}
  if r["prior_evidence_strength"].startswith("CONTEXTUAL"):
   item["decision_state"]="HUMAN_GOVERNED_SEMANTIC_DECISION_REQUIRED"
   item["allowed_decisions"]=["ADOPT_CONTEXTUAL_CANDIDATE","KEEP_UNRESOLVED"]
   contextual.append(item)
  else:
   item["decision_state"]="INSUFFICIENT_EVIDENCE_KEEP_UNRESOLVED"
   item["allowed_decisions"]=["KEEP_UNRESOLVED"]
   unresolved.append(item)
 return {"schema":"oce.p159.occ1k.r9y.governed.residual.semantic.binding.dossier.v1","milestone":"P159/OCC-1K-R9Y",
 "status":"HUMAN_GOVERNED_RESIDUAL_SEMANTIC_DECISION_REQUIRED",
 "input_r9x_sha256":sha(X),"contextual_cases":contextual,"unresolved_cases":unresolved,
 "counts":{"contextual":len(contextual),"unresolved":len(unresolved),"bindings_adopted":0},
 "decision_policy":{"bulk_automatic_adoption":False,"per_case_traceability_required":True,
 "contextual_candidate_is_not_source_proof":True,"human_governance_may_adopt_only_as_explicit_semantic_contract_decision":True,
 "unresolved_case_cannot_be_promoted":True,
 "confirmation_token_for_contextual_set":"I_CONFIRM_R9Y_ADOPT_CONTEXTUAL_CANDIDATES_AS_GOVERNED_SEMANTIC_CONTRACT"},
 "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"runtime_binding_created":False,
 "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
 "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
 "next_if_confirmed":"R9Z_ATOMIC_GOVERNED_CONTEXTUAL_BINDING_COMMIT",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9Y_GOVERNED_RESIDUAL_SEMANTIC_BINDING_DOSSIER_COMPLETE")
 print("STATUS="+d["status"]);print("CONTEXTUAL_CASES=%d/14"%c["contextual"]);print("UNRESOLVED_CASES=%d/1"%c["unresolved"])
 print("BINDINGS_ADOPTED=0");print("BULK_AUTOMATIC_ADOPTION=false");print("PER_CASE_TRACEABILITY_REQUIRED=true")
 print("UNRESOLVED_PROMOTABLE=false");print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("NEXT_IF_CONFIRMED="+d["next_if_confirmed"])
 print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
