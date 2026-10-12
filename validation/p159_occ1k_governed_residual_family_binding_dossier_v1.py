from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9Q=ROOT/"validation_artifacts/p159/occ1k_r9q/residual_rule_consumer_semantic_resolution_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9r/governed_residual_family_binding_dossier_v1.json"
def load(): return json.loads(R9Q.read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build():
 q=load(); families=[]
 for f in q["families"]:
  uniform=bool(f["uniform_candidate_set"])
  candidates=list(f["candidate_set"]) if uniform else []
  # Grouping establishes review scope only. It cannot prove a consumer.
  families.append({"family":f["family"],"rule_count":f["rule_count"],"rule_ids":f["rule_ids"],
   "candidate_set_for_review":candidates,"uniform_candidate_set":uniform,
   "proven_additional_consumers":[],
   "decision_state":"SOURCE_SEMANTIC_EVIDENCE_REQUIRED",
   "automatic_family_binding_permitted":False})
 return {"schema":"oce.p159.occ1k.r9r.governed.residual.family.binding.dossier.v1",
  "milestone":"P159/OCC-1K-R9R","status":"GOVERNED_RESIDUAL_FAMILY_DOSSIER_READY_SOURCE_EVIDENCE_REQUIRED",
  "input_r9q_sha256":sha(R9Q),"families":families,
  "counts":{"families":len(families),"rules":sum(x["rule_count"] for x in families),
            "families_with_proven_additional_consumer":sum(bool(x["proven_additional_consumers"]) for x in families)},
  "decision":{"automatic_adoption":False,"default":"KEEP_RESIDUALS_UNRESOLVED"},
  "semantics":{"family_membership_is_not_consumer_evidence":True,
   "uniform_candidate_set_is_not_binding_evidence":True,"candidate_is_not_binding":True,
   "source_semantic_evidence_required_before_adoption":True,"unknown_preserved":True},
  "boundaries":{"binding_layer_modified":False,"cnp_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
  "next_required_step":"R9S_SOURCE_BACKED_RESIDUAL_FAMILY_SEMANTIC_EVIDENCE_AUDIT",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9R_GOVERNED_RESIDUAL_FAMILY_BINDING_DOSSIER_COMPLETE")
 print("STATUS="+d["status"]);print("FAMILIES=%d/4"%c["families"]);print("RULES=%d/24"%c["rules"])
 print("FAMILIES_WITH_PROVEN_ADDITIONAL_CONSUMER=%d"%c["families_with_proven_additional_consumer"])
 print("AUTOMATIC_ADOPTION=false");print("BINDING_LAYER_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("DEFAULT_DECISION=KEEP_RESIDUALS_UNRESOLVED")
 print("NEXT="+d["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
