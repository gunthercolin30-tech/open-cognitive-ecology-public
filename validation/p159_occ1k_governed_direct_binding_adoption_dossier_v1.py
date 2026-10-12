from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9U=ROOT/"validation_artifacts/p159/occ1k_r9u/subgroup_consumer_source_evidence_resolution_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9v/governed_direct_binding_adoption_dossier_v1.json"
def load():return json.loads(R9U.read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build():
 u=load(); direct=[]; deferred=[]
 for x in u["subgroups"]:
  if x["evidence_strength"]=="DIRECT_SEMANTIC_ROLE_MATCH":
   direct.append({"subgroup_id":x["subgroup_id"],"rule_ids":x["rule_ids"],
    "source_object_id":x["source_object_id"],"proposed_consumers":x["candidate_consumers"],
    "evidence_ids":x["evidence_ids"],"decision_state":"READY_FOR_HUMAN_GOVERNED_ADOPTION",
    "binding_adopted":False})
  else:
   deferred.append({"subgroup_id":x["subgroup_id"],"rule_ids":x["rule_ids"],
    "evidence_strength":x["evidence_strength"],"decision_state":"DEFERRED_NOT_PART_OF_R9V"})
 return {"schema":"oce.p159.occ1k.r9v.governed.direct.binding.adoption.dossier.v1",
  "milestone":"P159/OCC-1K-R9V","status":"HUMAN_GOVERNED_DIRECT_BINDING_ADOPTION_DECISION_REQUIRED",
  "input_r9u_sha256":sha(R9U),"direct_candidates":direct,"deferred":deferred,
  "counts":{"direct_subgroups":len(direct),"direct_rules":sum(len(x["rule_ids"]) for x in direct),
   "deferred_subgroups":len(deferred)},
  "decision":{"choices":["ADOPT_DIRECT_BINDINGS_ONLY","KEEP_DIRECT_BINDINGS_UNRESOLVED"],
   "default":"KEEP_DIRECT_BINDINGS_UNRESOLVED","automatic_adoption":False,
   "confirmation_token_for_adoption":"I_CONFIRM_R9V_ADOPT_DIRECT_BINDINGS_ONLY"},
  "semantics":{"direct_semantic_role_match_is_candidate_not_authorization":True,
   "contextual_cases_excluded_from_this_decision":True,"unresolved_cases_excluded_from_this_decision":True,
   "compilation_not_authorization":True,"unknown_preserved":True},
  "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"p160b_opened":False},
  "next_if_adopted":"R9W_ATOMIC_GOVERNED_DIRECT_BINDING_COMMIT",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9V_GOVERNED_DIRECT_BINDING_ADOPTION_DOSSIER_COMPLETE")
 print("STATUS="+d["status"]);print("DIRECT_SUBGROUPS=%d/6"%c["direct_subgroups"])
 print("DIRECT_RULES=%d"%c["direct_rules"]);print("DEFERRED_SUBGROUPS=%d/15"%c["deferred_subgroups"])
 print("AUTOMATIC_ADOPTION=false");print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("DEFAULT_DECISION="+d["decision"]["default"])
 print("NEXT_IF_ADOPTED="+d["next_if_adopted"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
