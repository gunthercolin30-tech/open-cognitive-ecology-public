from __future__ import annotations
from pathlib import Path
from copy import deepcopy
from typing import Any,Mapping
import hashlib,json,os,tempfile,threading
from ontology.p161_authorization_token_lifecycle import TERMINAL,initialize_lifecycle,refresh,reserve_for_use,consume_reserved,revoke

def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def h(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def atomic(path,obj,filesystem_effect_context=None):
 path=Path(path)
 if filesystem_effect_context is None:raise RuntimeError("p161_atomic_filesystem_effect_context_required")
 payload=(json.dumps(obj,sort_keys=True,indent=2)+"\n").encode("utf-8")
 filesystem_effect_context.begin()
 if not path.parent.exists():
  filesystem_effect_context.execute_path("p161_atomic_create_dirs","FS_CREATE_DIRS",path.parent)
 filesystem_effect_context.execute_path("p161_atomic_write_replace","FS_WRITE_REPLACE_BYTES",path,payload)

class TokenStore:
 def __init__(self,root,filesystem_effect_context=None):
  self.dir=Path(root)/"store"
  if not self.dir.exists():
   if filesystem_effect_context is None:raise RuntimeError("governed_store_filesystem_effect_context_required")
   filesystem_effect_context.begin()
   filesystem_effect_context.execute_path("p161_store_create_dirs","FS_CREATE_DIRS",self.dir)
 def persist(self,t,filesystem_effect_context=None):
  tid=t["body"]["token_id"];p=self.dir/(tid+".json")
  if p.exists():
   old=json.loads(p.read_text())
   if h(old)!=h(t):raise ValueError("IMMUTABLE_TOKEN_CONFLICT")
   return tid
  atomic(p,deepcopy(t),filesystem_effect_context);return tid
 def load(self,tid):return json.loads((self.dir/(tid+".json")).read_text())

class TokenJournal:
 def __init__(self,root,filesystem_effect_context=None):
  self.path=Path(root)/"journal.jsonl"
  if not self.path.parent.exists():
   if filesystem_effect_context is None:raise RuntimeError("governed_filesystem_effect_context_required")
   filesystem_effect_context.begin()
   filesystem_effect_context.execute_path("archive_create_dirs","FS_CREATE_DIRS",self.path.parent)
 def entries(self):
  if not self.path.exists():return []
  return [json.loads(x) for x in self.path.read_text().splitlines() if x.strip()]
 def append(self,eid,payload):
  es=self.entries()
  for e in es:
   if e["event_id"]==eid:
    if h(e["payload"])!=h(payload):raise ValueError("EVENT_ID_CONFLICT")
    return deepcopy(e)
  prev=es[-1]["journal_hash"] if es else "GENESIS";e={"event_id":eid,"previous_journal_hash":prev,"payload":deepcopy(payload)}
  e["journal_hash"]=h(e)
  with self.path.open("a") as f:f.write(canon(e)+"\n");f.flush();os.fsync(f.fileno())
  return e
 def verify(self):
  prev="GENESIS"
  for e in self.entries():
   if e.get("previous_journal_hash")!=prev:return False
   x=dict(e);claimed=x.pop("journal_hash",None)
   if claimed!=h(x):return False
   prev=claimed
  return True

class TokenRegistry:
 def __init__(self,root):self.path=Path(root)/"registry.json";self.state={"version":0,"tokens":{}}
 def write(self,state,filesystem_effect_context=None):self.state=deepcopy(state);atomic(self.path,self.state,filesystem_effect_context)
 def load(self):
  if self.path.exists():self.state=json.loads(self.path.read_text())
  return deepcopy(self.state)

class P161JRuntime:
 def __init__(self,root,store_filesystem_effect_context=None,root_filesystem_effect_context=None,registry_filesystem_effect_context=None):
  self.root=Path(root)
  if not self.root.exists():
   if root_filesystem_effect_context is None:raise RuntimeError("governed_runtime_root_filesystem_effect_context_required")
   root_filesystem_effect_context.begin()
   root_filesystem_effect_context.execute_path("p161_runtime_root_create_dirs","FS_CREATE_DIRS",self.root)
  self.store=TokenStore(root,store_filesystem_effect_context);self.journal=TokenJournal(root);self.registry=TokenRegistry(root);self.lock=threading.RLock();self.reconstruct(registry_filesystem_effect_context)
 def _event(self,eid,typ,tid,data):
  return self.journal.append(eid,{"type":typ,"token_id":tid,"data":deepcopy(data)})
 def commit_token(self,token,event_id,*,max_uses=None,crash_after=None,store_filesystem_effect_context=None,registry_filesystem_effect_context=None):
  with self.lock:
   tid=token["body"]["token_id"]
   self._event(event_id+":PREPARE","STAGE",tid,{"stage":"PREPARE","usable":False})
   if crash_after=="PREPARE":raise RuntimeError("SIMULATED_CRASH")
   self._event(event_id+":VALIDATE","STAGE",tid,{"stage":"VALIDATE","usable":False})
   if crash_after=="VALIDATE":raise RuntimeError("SIMULATED_CRASH")
   self._event(event_id+":SIGN","STAGE",tid,{"stage":"SIGN","usable":False})
   if crash_after=="SIGN":raise RuntimeError("SIMULATED_CRASH")
   self.store.persist(token,store_filesystem_effect_context)
   if crash_after=="STORE":raise RuntimeError("SIMULATED_CRASH")
   lc=initialize_lifecycle(token,max_uses=max_uses)
   self._event(event_id+":COMMIT","COMMIT",tid,{"token_hash":token["token_hash"],"lifecycle":lc})
   if crash_after=="JOURNAL":raise RuntimeError("SIMULATED_CRASH")
   self.reconstruct(registry_filesystem_effect_context)
   if crash_after=="REGISTRY":raise RuntimeError("SIMULATED_CRASH")
   return {"status":"TOKEN_COMMITTED","token_id":tid,"execution_performed":False,"p162_opened":False}
 def reconstruct(self,filesystem_effect_context=None):
  state={"version":0,"tokens":{}}
  if not self.journal.verify():return {"status":"AUTHORIZATION_CONTINUITY_UNCERTAIN","issues":["JOURNAL_INVALID"]}
  for e in self.journal.entries():
   p=e["payload"];tid=p["token_id"]
   if p["type"]=="COMMIT":
    try:self.store.load(tid)
    except Exception:return {"status":"AUTHORIZATION_CONTINUITY_UNCERTAIN","issues":["STORE_MISSING:"+tid]}
    state["tokens"][tid]={"lifecycle":deepcopy(p["data"]["lifecycle"]),"journal_hash":e["journal_hash"]}
   elif p["type"]=="LIFECYCLE" and tid in state["tokens"]:
    old=state["tokens"][tid]["lifecycle"];new=deepcopy(p["data"]["lifecycle"])
    if old.get("state") in TERMINAL and new.get("state")!=old.get("state"):return {"status":"AUTHORIZATION_CONTINUITY_UNCERTAIN","issues":["TERMINAL_RESURRECTION:"+tid]}
    state["tokens"][tid]={"lifecycle":new,"journal_hash":e["journal_hash"]}
  state["version"]=len(self.journal.entries());self.registry.write(state,filesystem_effect_context);return {"status":"RECONSTRUCTED","state":deepcopy(state)}
 def lifecycle(self,tid):return deepcopy(self.registry.state["tokens"][tid]["lifecycle"])
 def reserve(self,tid,*,now,reservation_id,event_id,revalidation_passed=False,registry_filesystem_effect_context=None):
  with self.lock:
   token=self.store.load(tid);lc=self.lifecycle(tid);r=reserve_for_use(lc,token,now=now,reservation_id=reservation_id,current_token_hash=token["token_hash"],revalidation_passed=revalidation_passed)
   if r["status"]!="RESERVED":return r
   self._event(event_id,"LIFECYCLE",tid,{"lifecycle":r["lifecycle"]});self.reconstruct(registry_filesystem_effect_context);return r
 def consume(self,tid,*,now,reservation_id,event_id,registry_filesystem_effect_context=None):
  with self.lock:
   r=consume_reserved(self.lifecycle(tid),now=now,reservation_id=reservation_id)
   if r["status"]!="CONSUMED_USE":return r
   self._event(event_id,"LIFECYCLE",tid,{"lifecycle":r["lifecycle"]});self.reconstruct(registry_filesystem_effect_context);return r
 def revoke(self,tid,*,now,reason,event_id,registry_filesystem_effect_context=None):
  with self.lock:
   x=revoke(self.lifecycle(tid),now=now,reason=reason);self._event(event_id,"LIFECYCLE",tid,{"lifecycle":x});self.reconstruct(registry_filesystem_effect_context);return x

# P161_CANONICAL_COMPLETION_AFGH_V1
IDEMPOTENCY_CLASSES=("ISSUANCE","RESERVATION","CONSUMPTION","REVOCATION")
CONSUMPTION_INDETERMINATE="CONSUMPTION_INDETERMINATE"
PARTIAL_EFFECT="PARTIAL_EFFECT"
FAILED_AFTER_EFFECT="FAILED_AFTER_EFFECT"
def classify_consumption_recovery(*,commit_known,effect_known):
    if not commit_known or not effect_known:return {"status":CONSUMPTION_INDETERMINATE,"retry_allowed":False}
    return {"status":"DETERMINATE","retry_allowed":True}
