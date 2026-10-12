from pathlib import Path
import json, hashlib, os, tempfile
ROOT=Path.home()/"open-cognitive-ecology"
DOSSIER=ROOT/"validation_artifacts/p159/occ1k_r9l/governed_consumer_semantic_contract_dossier_v1.json"
OUTDIR=ROOT/"validation_artifacts/p159/occ1k_r9m"
CONTRACT=OUTDIR/"governed_consumer_semantic_contract_v1.json"
RECEIPT=OUTDIR/"atomic_governed_consumer_semantic_contract_commit_receipt_v1.json"
TOKEN="I_CONFIRM_R9L_ADOPT_CONTRACT"
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_dossier():
 d=json.loads(DOSSIER.read_text())
 if d.get("status")!="HUMAN_GOVERNED_CONSUMER_SEMANTIC_CONTRACT_DECISION_REQUIRED": raise RuntimeError("R9L_DOSSIER_NOT_READY")
 if d.get("consumer_count")!=6: raise RuntimeError("R9L_CONSUMER_COUNT_DIVERGENCE")
 return d
def build_contract():
 d=load_dossier()
 return {"schema":"oce.p159.occ1k.r9m.governed.consumer.semantic.contract.v1","milestone":"P159/OCC-1K-R9M",
 "status":"ADOPTED_GOVERNED_SEMANTIC_CONTRACT","source_dossier_sha256":sha_file(DOSSIER),
 "responsibilities":d["responsibilities"],"derivation_policy":d["derivation_policy"],
 "scope":{"semantic_responsibility_contract_only":True,"rule_bindings_modified":False,"runtime_reachability_claimed":False,
 "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False},
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def atomic_write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
 try:
  with os.fdopen(fd,"wb") as f:
   f.write(data); f.flush(); os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
def commit(token):
 if token!=TOKEN: raise RuntimeError("EXPLICIT_CONFIRMATION_REQUIRED")
 c=build_contract(); cb=canon(c)+b"\n"; ch=sha_bytes(cb)
 if CONTRACT.exists():
  if CONTRACT.read_bytes()!=cb: raise RuntimeError("EXISTING_CONTRACT_DIVERGENCE")
 else: atomic_write(CONTRACT,cb)
 receipt={"schema":"oce.p159.occ1k.r9m.atomic.commit.receipt.v1","milestone":"P159/OCC-1K-R9M","status":"COMMITTED",
 "decision":"ADOPT_CONTRACT","confirmation_token_sha256":sha_bytes(TOKEN.encode()),"source_dossier_sha256":sha_file(DOSSIER),
 "contract_sha256":ch,"history_preserved":True,"retroactive_repair":False,
 "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"canonical_source_modified":False,"runtime_binding_created":False,
 "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED_PENDING_RULE_BINDING_DERIVATION",
 "lock_ready":False,"lock_granted":False,"p160b_opened":False},
 "next_required_step":"R9N_SOURCE_BACKED_RULE_CONSUMER_BINDING_DERIVATION"}
 rb=canon(receipt)+b"\n"
 if RECEIPT.exists() and RECEIPT.read_bytes()!=rb: raise RuntimeError("EXISTING_RECEIPT_DIVERGENCE")
 if not RECEIPT.exists(): atomic_write(RECEIPT,rb)
 return receipt
def main(argv=None):
 import sys
 argv=sys.argv[1:] if argv is None else argv
 if len(argv)!=2 or argv[0]!="--confirm": raise SystemExit("USAGE: --confirm "+TOKEN)
 r=commit(argv[1])
 print("P159_OCC1K_R9M_ATOMIC_GOVERNED_CONSUMER_SEMANTIC_CONTRACT_COMMIT_COMPLETE")
 print("STATUS="+r["status"]); print("DECISION="+r["decision"]); print("CONSUMERS=6/6")
 print("HISTORY_PRESERVED=true"); print("RETROACTIVE_REPAIR=false"); print("RULE_BINDINGS_MODIFIED=false")
 print("RUNTIME_BINDING_CREATED=false"); print("RUNTIME_ENFORCEMENT_PROVEN=false"); print("AUTHORIZATION_CREATED=false")
 print("EXECUTION_PERFORMED=false"); print("FL_B3=BLOCKED_PENDING_RULE_BINDING_DERIVATION"); print("P160B_OPENED=false")
 print("NEXT="+r["next_required_step"]); print("CONTRACT_SHA256="+r["contract_sha256"]); print("RECEIPT_SHA256="+sha_file(RECEIPT))
if __name__=="__main__": main()
