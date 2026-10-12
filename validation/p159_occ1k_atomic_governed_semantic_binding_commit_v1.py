from pathlib import Path
import argparse,hashlib,json,os,tempfile
ROOT=Path.home()/"open-cognitive-ecology"
DOSSIER=ROOT/"validation_artifacts/p159/occ1k_r9f/governed_semantic_binding_adoption_dossier_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9g"
LAYER=OUT/"governed_semantic_binding_layer_v1.json"
RECEIPT=OUT/"atomic_governed_semantic_binding_commit_receipt_v1.json"
TOKEN="I_CONFIRM_R9F_ADOPT"
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_write(p,b):
 p.parent.mkdir(parents=True,exist_ok=True); fd,t=tempfile.mkstemp(prefix=p.name+".",suffix=".tmp",dir=str(p.parent))
 try:
  with os.fdopen(fd,"wb") as f: f.write(b); f.flush(); os.fsync(f.fileno())
  os.replace(t,p)
 finally:
  if os.path.exists(t): os.unlink(t)
def load():
 d=json.loads(DOSSIER.read_text())
 if d.get("status")!="HUMAN_GOVERNED_ADOPTION_DECISION_REQUIRED" or d.get("candidate_count")!=8 or not all(d.get("anchor_checks",{}).values()): raise RuntimeError("R9F_DOSSIER_INVALID")
 return d
def layer():
 d=load(); bs=[]
 for x in d["proposals"]:
  if sha(ROOT/x["source_path"])!=x["source_sha256"]: raise RuntimeError("SOURCE_DRIFT:"+x["candidate_id"])
  bs.append({**x,"binding_status":"ADOPTED_GOVERNED_SOURCE_BACKED_BINDING","runtime_authority_granted":False,"authorization_created":False,"execution_performed":False})
 bs.sort(key=lambda x:x["candidate_id"])
 r={"schema":"oce.p159.occ1k.r9g.binding_layer.v1","status":"ADOPTED","binding_count":8,"r9f_dossier_sha256":sha(DOSSIER),"bindings":bs,"historical_evidence_preserved":True,"retroactive_repair":False,"canonical_source_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED_PENDING_POST_ADOPTION_REPLAY","lock_ready":False,"lock_granted":False,"p160b_opened":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
 r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest(); return r
def preflight(): return {"status":"READY_FOR_EXPLICIT_CONFIRMATION","binding_count":layer()["binding_count"]}
def commit(confirm):
 if confirm!=TOKEN: raise RuntimeError("EXPLICIT_CONFIRMATION_REQUIRED")
 r=layer(); payload=canon(r)+b"\n"
 if LAYER.exists() and LAYER.read_bytes()!=payload: raise RuntimeError("DIVERGENT_EXISTING_R9G_LAYER")
 atomic_write(LAYER,payload)
 q={"schema":"oce.p159.occ1k.r9g.commit_receipt.v1","status":"COMMITTED","decision":"ADOPT","confirmation_token":TOKEN,"r9f_dossier_sha256":sha(DOSSIER),"adopted_layer_sha256":sha(LAYER),"binding_count":8,"historical_evidence_preserved":True,"retroactive_repair":False,"canonical_source_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED_PENDING_POST_ADOPTION_REPLAY","lock_ready":False,"lock_granted":False,"p160b_opened":False,"next_required_step":"R9H_POST_ADOPTION_INDEPENDENT_REPLAY","functional_conclusion_only":True,"phenomenology_undetermined":True}
 q["semantic_hash"]=hashlib.sha256(canon(q)).hexdigest(); atomic_write(RECEIPT,canon(q)+b"\n"); return q
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--confirm"); a=ap.parse_args()
 if not a.confirm:
  r=preflight(); print("P159_OCC1K_R9G_PREFLIGHT_OK\nSTATUS=READY_FOR_EXPLICIT_CONFIRMATION\nBINDINGS=8/8\nADOPTION_PERFORMED=false\nFL_B3=BLOCKED\nP160B_OPENED=false"); return
 r=commit(a.confirm); print("P159_OCC1K_R9G_ATOMIC_GOVERNED_SEMANTIC_BINDING_COMMIT_COMPLETE\nSTATUS=COMMITTED\nDECISION=ADOPT\nBINDINGS=8/8\nHISTORICAL_EVIDENCE_PRESERVED=true\nRETROACTIVE_REPAIR=false\nCANONICAL_SOURCE_MODIFIED=false\nRUNTIME_BINDING_CREATED=false\nRUNTIME_ENFORCEMENT_PROVEN=false\nAUTHORIZATION_CREATED=false\nEXECUTION_PERFORMED=false\nFL_B3=BLOCKED_PENDING_POST_ADOPTION_REPLAY\nLOCK_READY=false\nLOCK_GRANTED=false\nP160B_OPENED=false\nNEXT="+r["next_required_step"]+"\nRECEIPT_SHA256="+sha(RECEIPT))
if __name__=="__main__": main()
