from pathlib import Path
import json,hashlib,os,tempfile
ROOT=Path.home()/"open-cognitive-ecology"
DOSSIER=ROOT/"validation_artifacts/p159/occ1k_r9o/governed_rule_consumer_binding_dossier_v1.json"
OUTDIR=ROOT/"validation_artifacts/p159/occ1k_r9p"
LAYER=OUTDIR/"governed_proven_rule_consumer_binding_layer_v1.json"
RECEIPT=OUTDIR/"atomic_governed_proven_rule_consumer_binding_commit_receipt_v1.json"
TOKEN="I_CONFIRM_R9O_ADOPT_PROVEN_BINDINGS_ONLY"
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def shab(b):return hashlib.sha256(b).hexdigest()
def load():return json.loads(DOSSIER.read_text())
def build_layer():
 d=load()
 if d.get("status")!="HUMAN_GOVERNED_PARTIAL_BINDING_ADOPTION_DECISION_REQUIRED":raise RuntimeError("R9O_DOSSIER_NOT_READY")
 rows=[]
 for x in d["rules"]:
  rows.append({"rule_id":x["rule_id"],"source_norm_ids":x["source_norm_ids"],
   "adopted_consumers":list(x["proposed_consumers"]),
   "binding_state_at_adoption":x["binding_state"],
   "unresolved_reasons_preserved":list(x["unresolved_reasons"]),
   "candidate_not_adopted_consumers":list(x["candidate_not_adopted_consumers"])})
 return {"schema":"oce.p159.occ1k.r9p.governed.proven.rule.consumer.binding.layer.v1",
  "milestone":"P159/OCC-1K-R9P","status":"ADOPTED_PROVEN_BINDINGS_ONLY",
  "source_dossier_sha256":sha(DOSSIER),"rules":rows,
  "counts":{"rules":len(rows),"fully_resolved_adopted":sum(x["binding_state_at_adoption"]=="READY_FOR_GOVERNED_ADOPTION" for x in rows),
   "partial_preserved":sum(x["binding_state_at_adoption"]=="PARTIAL_KEEP_UNRESOLVED" for x in rows),
   "unresolved_preserved":sum(x["binding_state_at_adoption"]=="UNRESOLVED_NO_BINDING_PROPOSED" for x in rows)},
  "semantics":{"partial_adoption_is_not_full_resolution":True,"candidate_not_adopted_is_not_binding":True,
   "runtime_reachability_claimed":False,"runtime_enforcement_proven":False},
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def atomic(path,b):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
 try:
  with os.fdopen(fd,"wb") as f:f.write(b);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def commit(token):
 if token!=TOKEN:raise RuntimeError("EXPLICIT_CONFIRMATION_REQUIRED")
 layer=build_layer();lb=canon(layer)+b"\n"
 if LAYER.exists() and LAYER.read_bytes()!=lb:raise RuntimeError("EXISTING_LAYER_DIVERGENCE")
 if not LAYER.exists():atomic(LAYER,lb)
 receipt={"schema":"oce.p159.occ1k.r9p.atomic.commit.receipt.v1","milestone":"P159/OCC-1K-R9P","status":"COMMITTED",
  "decision":"ADOPT_PROVEN_BINDINGS_ONLY","source_dossier_sha256":sha(DOSSIER),"binding_layer_sha256":shab(lb),
  "history_preserved":True,"retroactive_repair":False,
  "counts":layer["counts"],"boundaries":{"cnp_modified":False,"runtime_binding_created":False,"runtime_reachability_claimed":False,
  "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED",
  "lock_ready":False,"lock_granted":False,"p160b_opened":False},
  "next_required_step":"R9Q_RESIDUAL_RULE_CONSUMER_SEMANTIC_RESOLUTION"}
 rb=canon(receipt)+b"\n"
 if RECEIPT.exists() and RECEIPT.read_bytes()!=rb:raise RuntimeError("EXISTING_RECEIPT_DIVERGENCE")
 if not RECEIPT.exists():atomic(RECEIPT,rb)
 return receipt
def main(argv=None):
 import sys
 a=sys.argv[1:] if argv is None else argv
 if len(a)!=2 or a[0]!="--confirm":raise SystemExit("USAGE: --confirm "+TOKEN)
 r=commit(a[1]);c=r["counts"]
 print("P159_OCC1K_R9P_ATOMIC_GOVERNED_PROVEN_BINDING_COMMIT_COMPLETE")
 print("STATUS="+r["status"]);print("DECISION="+r["decision"]);print("RULES=%d/48"%c["rules"])
 print("FULLY_RESOLVED_ADOPTED=%d"%c["fully_resolved_adopted"]);print("PARTIAL_PRESERVED=%d"%c["partial_preserved"]);print("UNRESOLVED_PRESERVED=%d"%c["unresolved_preserved"])
 print("HISTORY_PRESERVED=true");print("RETROACTIVE_REPAIR=false");print("RUNTIME_BINDING_CREATED=false")
 print("RUNTIME_ENFORCEMENT_PROVEN=false");print("AUTHORIZATION_CREATED=false");print("EXECUTION_PERFORMED=false")
 print("FL_B3=BLOCKED");print("P160B_OPENED=false");print("NEXT="+r["next_required_step"])
 print("LAYER_SHA256="+r["binding_layer_sha256"]);print("RECEIPT_SHA256="+sha(RECEIPT))
if __name__=="__main__":main()
