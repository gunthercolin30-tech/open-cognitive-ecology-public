from pathlib import Path
import json,hashlib,os,tempfile
ROOT=Path.home()/"open-cognitive-ecology"
Y=ROOT/"validation_artifacts/p159/occ1k_r9y/governed_residual_semantic_binding_dossier_v1.json"
W=ROOT/"validation_artifacts/p159/occ1k_r9w/governed_direct_rule_consumer_binding_layer_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9z"
LAYER=OUT/"governed_contextual_rule_consumer_binding_layer_v1.json"
RECEIPT=OUT/"atomic_governed_contextual_binding_commit_receipt_v1.json"
TOKEN="I_CONFIRM_R9Y_ADOPT_CONTEXTUAL_CANDIDATES_AS_GOVERNED_SEMANTIC_CONTRACT"
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cb(o):return (json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
def aw(p,b):
 p.parent.mkdir(parents=True,exist_ok=True);fd,t=tempfile.mkstemp(prefix=p.name+".",dir=str(p.parent))
 try:
  with os.fdopen(fd,"wb") as f:f.write(b);f.flush();os.fsync(f.fileno())
  os.replace(t,p)
 finally:
  if os.path.exists(t):os.unlink(t)
def build():
 y=load(Y);w=load(W)
 if y["status"]!="HUMAN_GOVERNED_RESIDUAL_SEMANTIC_DECISION_REQUIRED":raise RuntimeError("R9Y_NOT_READY")
 if len(y["contextual_cases"])!=14 or len(y["unresolved_cases"])!=1:raise RuntimeError("R9Y_PARTITION_MISMATCH")
 direct={b["rule_id"] for b in w["bindings"]}; bindings=[];seen=set()
 for c in y["contextual_cases"]:
  if not c["candidate_consumers"]:raise RuntimeError("CONTEXTUAL_CASE_WITHOUT_CANDIDATE")
  for rid in c["rule_ids"]:
   if rid in direct:raise RuntimeError("DIRECT_RULE_REUSE:"+rid)
   if rid in seen:raise RuntimeError("DUPLICATE_CONTEXTUAL_RULE:"+rid)
   seen.add(rid);bindings.append({"rule_id":rid,"subgroup_id":c["subgroup_id"],"source_object_id":c.get("source_object_id"),
    "consumers":c["candidate_consumers"],"evidence_ids":c.get("evidence_ids",[]),
    "binding_basis":"NEW_GOVERNED_SEMANTIC_CONTRACT_DECISION_NOT_RETROACTIVE_SOURCE_PROOF"})
 unresolved=[r for c in y["unresolved_cases"] for r in c["rule_ids"]]
 return {"schema":"oce.p159.occ1k.r9z.governed.contextual.rule.consumer.binding.layer.v1","milestone":"P159/OCC-1K-R9Z",
 "status":"COMMITTED","decision":"ADOPT_CONTEXTUAL_CANDIDATES_AS_GOVERNED_SEMANTIC_CONTRACT",
 "input_r9y_sha256":sha(Y),"preserved_r9w_sha256":sha(W),"bindings":sorted(bindings,key=lambda x:x["rule_id"]),
 "unresolved_rules_preserved":unresolved,
 "counts":{"contextual_subgroups_adopted":14,"contextual_rules_adopted":len(bindings),"unresolved_subgroups_preserved":1,"unresolved_rules_preserved":len(unresolved)},
 "semantics":{"new_contract_effect_prospective":True,"retroactive_source_proof_claimed":False,"r9w_preserved":True,"unresolved_promoted":False},
 "boundaries":{"cnp_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,
 "execution_performed":False,"fl_b3":"BLOCKED_PENDING_UNRESOLVED_AND_CHECKER_REPLAY","lock_ready":False,"p160b_opened":False},
 "next_required_step":"R9AA_UNRESOLVED_GENESIS_G0_RESOLUTION","functional_conclusion_only":True,"phenomenology_undetermined":True}
def commit(confirm):
 if confirm!=TOKEN:raise RuntimeError("EXPLICIT_CONFIRMATION_REQUIRED")
 d=build();lb=cb(d);r={"schema":"oce.p159.occ1k.r9z.atomic.governed.contextual.binding.commit.receipt.v1","status":"COMMITTED",
 "decision":d["decision"],"confirmation_token_verified":True,"r9y_sha256":sha(Y),"binding_layer_sha256":hashlib.sha256(lb).hexdigest(),
 "r9w_preserved":True,"unresolved_promoted":False,"runtime_binding_created":False,"authorization_created":False,"execution_performed":False,"p160b_opened":False}
 rb=cb(r)
 for p,b in ((LAYER,lb),(RECEIPT,rb)):
  if p.exists() and p.read_bytes()!=b:raise RuntimeError("DIVERGENT_EXISTING_ARTIFACT:"+str(p))
  aw(p,b)
 return d,hashlib.sha256(lb).hexdigest(),hashlib.sha256(rb).hexdigest()
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument("--confirm",required=True);q=a.parse_args()
 d,lh,rh=commit(q.confirm);c=d["counts"]
 print("P159_OCC1K_R9Z_ATOMIC_GOVERNED_CONTEXTUAL_BINDING_COMMIT_COMPLETE")
 print("STATUS=COMMITTED");print("CONTEXTUAL_SUBGROUPS_ADOPTED=%d/14"%c["contextual_subgroups_adopted"])
 print("CONTEXTUAL_RULES_ADOPTED=%d"%c["contextual_rules_adopted"]);print("UNRESOLVED_SUBGROUPS_PRESERVED=1/1")
 print("RETROACTIVE_SOURCE_PROOF_CLAIMED=false");print("R9W_PRESERVED=true");print("UNRESOLVED_PROMOTED=false")
 print("RUNTIME_BINDING_CREATED=false");print("AUTHORIZATION_CREATED=false");print("EXECUTION_PERFORMED=false")
 print("FL_B3=BLOCKED_PENDING_UNRESOLVED_AND_CHECKER_REPLAY");print("P160B_OPENED=false")
 print("NEXT="+d["next_required_step"]);print("LAYER_SHA256="+lh);print("RECEIPT_SHA256="+rh)
if __name__=="__main__":main()
