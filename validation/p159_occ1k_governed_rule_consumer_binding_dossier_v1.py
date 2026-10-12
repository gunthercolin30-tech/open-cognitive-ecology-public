from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9N=ROOT/"validation_artifacts/p159/occ1k_r9n/source_backed_rule_consumer_derivation_audit_v1.json"
CONTRACT=ROOT/"validation_artifacts/p159/occ1k_r9m/governed_consumer_semantic_contract_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9o/governed_rule_consumer_binding_dossier_v1.json"
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 n=load(R9N); c=load(CONTRACT)
 rows=[]
 for r in n["rules"]:
  guaranteed=list(r["guaranteed_contract_consumers"])
  unresolved=list(r["unresolved_reasons"])
  if not unresolved:
   state="READY_FOR_GOVERNED_ADOPTION"
   proposed=guaranteed
  elif guaranteed:
   state="PARTIAL_KEEP_UNRESOLVED"
   proposed=guaranteed
  else:
   state="UNRESOLVED_NO_BINDING_PROPOSED"
   proposed=[]
  rows.append({"rule_id":r["rule_id"],"source_norm_ids":r["source_norm_ids"],
   "binding_state":state,"proposed_consumers":proposed,
   "candidate_not_adopted_consumers":r["candidate_not_adopted_consumers"],
   "unresolved_reasons":unresolved})
 counts={"rules":len(rows),
   "ready_for_governed_adoption":sum(x["binding_state"]=="READY_FOR_GOVERNED_ADOPTION" for x in rows),
   "partial_keep_unresolved":sum(x["binding_state"]=="PARTIAL_KEEP_UNRESOLVED" for x in rows),
   "unresolved_no_binding_proposed":sum(x["binding_state"]=="UNRESOLVED_NO_BINDING_PROPOSED" for x in rows)}
 return {"schema":"oce.p159.occ1k.r9o.governed.rule.consumer.binding.dossier.v1",
  "milestone":"P159/OCC-1K-R9O","status":"HUMAN_GOVERNED_PARTIAL_BINDING_ADOPTION_DECISION_REQUIRED",
  "inputs":{"r9n_sha256":sha(R9N),"consumer_contract_sha256":sha(CONTRACT)},
  "decision":{"allowed":["ADOPT_PROVEN_BINDINGS_ONLY","KEEP_ALL_UNRESOLVED"],
              "default":"KEEP_ALL_UNRESOLVED","automatic_adoption":False},
  "counts":counts,"rules":rows,
  "semantics":{"partial_adoption_does_not_resolve_remaining_consumers":True,
   "candidate_not_adopted_is_not_binding":True,"unknown_preserved":True,
   "no_keyword_only_binding":True,"no_runtime_reachability_claim":True},
  "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,"p160b_opened":False},
  "next_if_adopt":"R9P_ATOMIC_GOVERNED_PROVEN_RULE_CONSUMER_BINDING_COMMIT",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build();OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode();OUT.write_bytes(b)
 return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write();c=d["counts"]
 print("P159_OCC1K_R9O_GOVERNED_RULE_CONSUMER_BINDING_DOSSIER_COMPLETE")
 print("STATUS="+d["status"]);print("RULES=%d/48"%c["rules"])
 print("READY_FOR_GOVERNED_ADOPTION=%d"%c["ready_for_governed_adoption"])
 print("PARTIAL_KEEP_UNRESOLVED=%d"%c["partial_keep_unresolved"])
 print("UNRESOLVED_NO_BINDING_PROPOSED=%d"%c["unresolved_no_binding_proposed"])
 print("AUTOMATIC_ADOPTION=false");print("RULE_BINDINGS_MODIFIED=false");print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("DEFAULT_DECISION=KEEP_ALL_UNRESOLVED")
 print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
